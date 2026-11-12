const API_BASE_URL = 'http://localhost:8000';

export class VoiceService {
  static async speechToText(audioBlob: Blob): Promise<string | null> {
    const formData = new FormData();
    formData.append('file', audioBlob, 'recording.wav');

    try {
      const response = await fetch(`${API_BASE_URL}/voice/stt`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        return data.text;
      }
    } catch (error) {
      console.error('STT Error:', error);
    }
    return null;
  }

  static async textToSpeech(text: string): Promise<HTMLAudioElement | null> {
    try {
      const response = await fetch(`${API_BASE_URL}/voice/tts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text }),
      });

      if (response.ok) {
        const audioBlob = await response.blob();
        const url = URL.createObjectURL(audioBlob);
        return new Audio(url);
      } else {
        console.error('TTS API error:', response.status, response.statusText);
      }
    } catch (error) {
      console.error('TTS Error:', error);
    }
    return null;
  }
}
