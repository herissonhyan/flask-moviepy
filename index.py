import base64
from flask import Flask, request, jsonify
from moviepy import TextClip, concatenate_videoclips, CompositeVideoClip, ImageClip, AudioFileClip
from gtts import gTTS
import io

app = Flask(__name__)

def add_newline(text, x):
    words = text.split()
    lines = [' '.join(words[i:i + x]) for i in range(0, len(words), x)]
    return '\n'.join(lines)

@app.route('/generate_quiz_video', methods=['POST'])
def generate_quiz_video():
    try:
        data = request.json
        question = data['pergunta']
        options = {
            "a": data['a'],
            "b": data['b'],
            "c": data['c'],
            "d": data['d']
        }
        correct_option = data['response']

        # Gerar áudio de "Bem-vindo" como bytes
        tts = gTTS('Bem-vindo ao Quiz!', lang='pt')
        audio_bem_vindo = io.BytesIO()
        tts.save(audio_bem_vindo)
        audio_bem_vindo.seek(0)  # Voltar para o início do arquivo em memória

        # Gerar áudio da pergunta como bytes
        tts = gTTS(question, lang='pt')
        audio_pergunta = io.BytesIO()
        tts.save(audio_pergunta)
        audio_pergunta.seek(0)  # Voltar para o início do arquivo em memória

        # Gerar áudio da resposta correta como bytes
        tts = gTTS(f"A resposta é {options[correct_option]}", lang='pt')
        audio_resposta = io.BytesIO()
        tts.save(audio_resposta)
        audio_resposta.seek(0)  # Voltar para o início do arquivo em memória

        video_width = 832
        video_height = 1472

        def create_introduction(text, font_size, color, duration, audio_clip):
            background = ImageClip("background.png")
            audio_clip.seek(0)  # Certificar-se que o áudio está no início
            return CompositeVideoClip([background, TextClip(text=text, font_size=font_size, color=color, size=(video_width, video_height), font='arial_narrow_7.ttf', text_align="center", stroke_color=(0, 0, 0), stroke_width=2)]).with_duration(duration).with_audio(audio_clip)

        def create_text_question(text_question, text_options, color, duration, audio_clip):
            background = ImageClip("background.png")
            audio_clip.seek(0)  # Certificar-se que o áudio está no início
            return CompositeVideoClip([background, TextClip(text=text_question + "\n\n" + text_options, color=color, size=(video_width, video_height), font='arial_narrow_7.ttf', text_align="center", stroke_color=(0, 0, 0), stroke_width=2)]).with_duration(duration).with_audio(audio_clip)

        def create_response(text, font_size, color, duration, audio_clip):
            background = ImageClip("background.png")
            audio_clip.seek(0)  # Certificar-se que o áudio está no início
            return CompositeVideoClip([background, TextClip(text=text, font_size=font_size, color=color, size=(video_width, video_height), font='arial_narrow_7.ttf', text_align="center", stroke_color=(0, 0, 0), stroke_width=2)]).with_duration(duration).with_audio(audio_clip)

        intro = create_introduction("Bem-vindo ao quiz", 100, "#fff", 3, AudioFileClip(audio_bem_vindo))
        options_str = "\n".join([f"{key.upper()}: {value}" for key, value in options.items()])
        word_count = len(question.split())
        question_clip = create_text_question(add_newline(question, 4), options_str, "#fff", (word_count * 1), AudioFileClip(audio_pergunta))
        word_count = len(options[correct_option].split())
        final = create_response(f"A resposta correta é: \n\n {options[correct_option]}", 100, "#fff", (word_count * 1), AudioFileClip(audio_resposta))

        # Concatenando os clipes
        final_clip = concatenate_videoclips([intro, question_clip, final])

        # Caminho de saída no diretório /tmp
        output_path = "/tmp/quiz_video.mp4"
        final_clip.write_videofile(output_path, fps=24, codec="libx264")

        # Convertendo o vídeo para base64
        with open(output_path, "rb") as video_file:
            video_base64 = base64.b64encode(video_file.read()).decode('utf-8')

        # Retornando a resposta com o vídeo em base64
        return jsonify({"message": "Vídeo gerado com sucesso!", "video_base64": video_base64})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
