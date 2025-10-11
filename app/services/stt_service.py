from .model_loader import get_audio_to_text_model
import logging
import librosa
import numpy as np
import json
from typing import Dict, List, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def chunk_audio(audio) -> list[tuple[float, float, np.ndarray]]:
    """Chunks audio into 30 second segments with 2 second overlap"""
    chunk_size = 30
    overlap = 2
    sample_rate = 16000
    total_seconds = len(audio) / sample_rate
    segments = []

    logger.info(f"Total seconds: {total_seconds}")
    logger.info(
        f"Number of segments: {len(np.arange(0, total_seconds, chunk_size - overlap))}"
    )

    # Calculate number of segments with overlap
    for start_time in np.arange(0, total_seconds, chunk_size - overlap):
        end_time = min(start_time + chunk_size, total_seconds)

        # Extract segment
        start_sample = int(start_time * sample_rate)
        end_sample = int(end_time * sample_rate)
        chunk = audio[start_sample:end_sample]

        if len(chunk) > 0:
            segments.append((start_time, end_time, chunk))

    return segments


def remove_overlapping_words(
    all_words: List[Dict], overlap_threshold: float = 1.5
) -> List[Dict]:
    """
    Remove duplicate words that occur due to chunk overlap.
    Words within overlap_threshold seconds of each other with similar content are considered duplicates.
    """
    if not all_words:
        return all_words

    # Sort words by start time
    sorted_words = sorted(all_words, key=lambda x: x["start"])
    filtered_words = []

    for i, word in enumerate(sorted_words):
        is_duplicate = False

        # Check against previous words within the overlap threshold
        for prev_word in filtered_words[-10:]:  # Check last 10 words for efficiency
            time_diff = abs(word["start"] - prev_word["end"])

            # If words are close in time and have similar content, consider it a duplicate
            if (
                time_diff <= overlap_threshold
                and word["word"].strip().lower() == prev_word["word"].strip().lower()
            ):
                is_duplicate = True
                break

        if not is_duplicate:
            filtered_words.append(word)

    return filtered_words


def merge_segments(segments: List[Dict]) -> List[Dict]:
    """
    Merge segments and remove overlapping words.
    """
    if not segments:
        return segments

    # Collect all words from all segments
    all_words = []
    for segment in segments:
        for word in segment.get("words", []):
            all_words.append(word)

    # Remove overlapping words
    filtered_words = remove_overlapping_words(all_words)

    # Reconstruct segments based on filtered words
    merged_segments = []
    current_segment = None

    for word in filtered_words:
        # If this is the first word or there's a significant gap, start a new segment
        if (
            current_segment is None or word["start"] - current_segment["end"] > 2.0
        ):  # 2 second gap threshold
            if current_segment is not None:
                merged_segments.append(current_segment)

            current_segment = {
                "start": word["start"],
                "end": word["end"],
                "text": word["word"],
                "confidence": word.get("confidence", 0),
                "words": [word],
            }
        else:
            # Add word to current segment
            current_segment["text"] += " " + word["word"]
            current_segment["end"] = word["end"]
            current_segment["words"].append(word)
            # Update confidence (average)
            current_segment["confidence"] = (
                current_segment["confidence"] * (len(current_segment["words"]) - 1)
                + word.get("confidence", 0)
            ) / len(current_segment["words"])

    # Add the last segment
    if current_segment is not None:
        merged_segments.append(current_segment)

    return merged_segments


def transcribe_audio(audio_file_path: str) -> Dict[str, Any]:
    """Transcribes audio chunks to text using Whisper model with detailed output and overlap removal."""
    try:
        # Load and preprocess audio
        audio, sr = librosa.load(audio_file_path, sr=16000, mono=True)
        logger.info(f"Loaded audio: {len(audio)} samples at {sr}Hz")

        # Chunk the audio
        chunks = chunk_audio(audio)
        logger.info(f"Created {len(chunks)} audio chunks")

        # Transcribe each chunk
        model = get_audio_to_text_model()
        all_segments = []
        detected_language = None
        full_text = ""

        for i, (start_time, end_time, chunk) in enumerate(chunks):
            logger.info(
                f"Transcribing chunk {i + 1}/{len(chunks)} ({start_time:.1f}s - {end_time:.1f}s)"
            )

            # Use transcribe with word_timestamps=True to get detailed output
            result = model.transcribe(
                chunk,
                word_timestamps=True,
                language=None,  # Let Whisper auto-detect language
            )

            # Store detected language from first chunk
            if detected_language is None:
                detected_language = result.get("language", "unknown")

            # Process segments with timestamps
            chunk_segments = []
            for segment in result.get("segments", []):
                segment_data = {
                    "start": start_time + segment["start"],  # Adjust for chunk offset
                    "end": start_time + segment["end"],  # Adjust for chunk offset
                    "text": segment["text"].strip(),
                    "confidence": segment.get("avg_logprob", 0),
                    "words": [],
                }

                # Add word-level timestamps if available
                for word in segment.get("words", []):
                    word_data = {
                        "word": word["word"],
                        "start": start_time + word["start"],  # Adjust for chunk offset
                        "end": start_time + word["end"],  # Adjust for chunk offset
                        "confidence": word.get("probability", 0),
                    }
                    segment_data["words"].append(word_data)

                chunk_segments.append(segment_data)

            all_segments.extend(chunk_segments)

        # Merge segments and remove overlapping words
        logger.info("Merging segments and removing overlapping words...")
        merged_segments = merge_segments(all_segments)

        # Reconstruct full text from merged segments
        full_text = " ".join([segment["text"] for segment in merged_segments])

        # Create comprehensive output
        output = {
            "detected_language": detected_language,
            "full_text": full_text,
            "total_duration": len(audio) / sr,
            "segments": merged_segments,
            "metadata": {
                "model": "whisper-large",
                "sample_rate": sr,
                "chunks_processed": len(chunks),
                "original_segments": len(all_segments),
                "merged_segments": len(merged_segments),
            },
        }

        return output

    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}")
        raise


def save_transcription_to_json(
    transcription_data: Dict[str, Any], output_path: str
) -> None:
    """Save transcription data to a JSON file."""
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(transcription_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Transcription saved to {output_path}")
    except Exception as e:
        logger.error(f"Error saving transcription to JSON: {str(e)}")
        raise
