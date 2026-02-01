"""
Transcript Parser - Handles multiple transcript formats
Supports: Plain text, SRT, VTT with speaker labels and timestamps
"""
import re
from typing import List, Dict, Optional
from datetime import timedelta


def parse_timestamp(timestamp_str: str) -> float:
    """Convert timestamp string to seconds (supports HH:MM:SS, MM:SS, SS formats)"""
    parts = timestamp_str.strip().split(':')
    parts = [float(p.replace(',', '.')) for p in parts]
    
    if len(parts) == 3:  # HH:MM:SS
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    elif len(parts) == 2:  # MM:SS
        return parts[0] * 60 + parts[1]
    else:  # SS
        return parts[0]


def format_timestamp(seconds: float) -> str:
    """Convert seconds to HH:MM:SS format"""
    td = timedelta(seconds=seconds)
    hours = int(td.total_seconds() // 3600)
    minutes = int((td.total_seconds() % 3600) // 60)
    secs = int(td.total_seconds() % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def parse_srt(content: str) -> List[Dict]:
    """Parse SRT subtitle format"""
    entries = []
    blocks = content.strip().split('\n\n')
    
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) < 3:
            continue
            
        # Parse timestamp line (e.g., "00:00:01,000 --> 00:00:04,000")
        timestamp_match = re.search(r'(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})', lines[1])
        if not timestamp_match:
            continue
            
        start_time = parse_timestamp(timestamp_match.group(1))
        end_time = parse_timestamp(timestamp_match.group(2))
        
        # Text is everything after the timestamp line
        text = ' '.join(lines[2:])
        
        # Try to extract speaker from text (e.g., "[Speaker 1]" or "Speaker 1:")
        speaker_match = re.match(r'\[?([^\]]+?)\]?:\s*(.*)', text)
        if speaker_match:
            speaker = speaker_match.group(1)
            text = speaker_match.group(2)
        else:
            speaker = "Unknown"
            
        entries.append({
            'start_time': start_time,
            'end_time': end_time,
            'speaker': speaker,
            'text': text.strip()
        })
    
    return entries


def parse_vtt(content: str) -> List[Dict]:
    """Parse VTT subtitle format"""
    # VTT is similar to SRT but starts with "WEBVTT"
    content = re.sub(r'^WEBVTT.*?\n\n', '', content, flags=re.DOTALL)
    return parse_srt(content)  # Use SRT parser after removing header


def parse_plain_text(content: str) -> List[Dict]:
    """Parse plain text with speaker labels and optional timestamps"""
    entries = []
    lines = content.strip().split('\n')
    
    current_speaker = "Unknown"
    current_time = 0.0
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Try to match: [HH:MM:SS] Speaker: Text or Speaker: Text
        timestamp_speaker_match = re.match(r'\[?(\d{1,2}:\d{2}(?::\d{2})?)\]?\s*([^:]+):\s*(.*)', line)
        speaker_only_match = re.match(r'([^:]+):\s*(.*)', line)
        
        if timestamp_speaker_match:
            timestamp = timestamp_speaker_match.group(1)
            speaker = timestamp_speaker_match.group(2).strip()
            text = timestamp_speaker_match.group(3).strip()
            current_time = parse_timestamp(timestamp)
            current_speaker = speaker
        elif speaker_only_match:
            speaker = speaker_only_match.group(1).strip()
            text = speaker_only_match.group(2).strip()
            current_speaker = speaker
        else:
            # Continuation of previous speaker
            text = line
            speaker = current_speaker
        
        if text:
            # Estimate duration based on text length (rough: 150 words per minute)
            word_count = len(text.split())
            duration = (word_count / 150) * 60
            
            entries.append({
                'start_time': current_time,
                'end_time': current_time + duration,
                'speaker': speaker,
                'text': text
            })
            
            current_time += duration
    
    return entries


def parse_transcript(content: str, file_format: Optional[str] = None) -> List[Dict]:
    """
    Main parser - auto-detects format or uses specified format
    
    Args:
        content: Raw transcript content
        file_format: Optional format hint ('srt', 'vtt', 'txt')
    
    Returns:
        List of transcript entries with start_time, end_time, speaker, text
    """
    content = content.strip()
    
    # Auto-detect format if not specified
    if file_format is None:
        if content.startswith('WEBVTT'):
            file_format = 'vtt'
        elif re.search(r'\d+\n\d{2}:\d{2}:\d{2},\d{3}\s*-->', content):
            file_format = 'srt'
        else:
            file_format = 'txt'
    
    # Parse based on format
    if file_format == 'srt':
        return parse_srt(content)
    elif file_format == 'vtt':
        return parse_vtt(content)
    else:
        return parse_plain_text(content)


def merge_entries(entries: List[Dict], max_gap: float = 2.0) -> List[Dict]:
    """
    Merge consecutive entries from the same speaker with small gaps
    
    Args:
        entries: List of transcript entries
        max_gap: Maximum gap in seconds to merge (default 2.0)
    
    Returns:
        Merged list of entries
    """
    if not entries:
        return []
    
    merged = []
    current = entries[0].copy()
    
    for entry in entries[1:]:
        # Merge if same speaker and small gap
        if (entry['speaker'] == current['speaker'] and 
            entry['start_time'] - current['end_time'] <= max_gap):
            current['end_time'] = entry['end_time']
            current['text'] += ' ' + entry['text']
        else:
            merged.append(current)
            current = entry.copy()
    
    merged.append(current)
    return merged


# Example usage and testing
if __name__ == "__main__":
    # Test plain text format
    sample_text = """
    [00:00:15] Joe Rogan: So you're telling me that AI is going to change everything?
    [00:00:20] Elon Musk: Absolutely. I think AI is the most important thing humanity has ever worked on.
    [00:00:28] Joe Rogan: That's a bold statement. Why do you think that?
    [00:00:32] Elon Musk: Because it's more profound than electricity or fire. It's going to amplify human capability by orders of magnitude.
    """
    
    entries = parse_transcript(sample_text)
    for entry in entries:
        print(f"[{format_timestamp(entry['start_time'])}] {entry['speaker']}: {entry['text'][:50]}...")
