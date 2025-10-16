import asyncio
import logging
import hashlib
import os
from typing import Any, Dict, Optional
from moviepy.video.fx.all import crossfadein
from google.cloud import texttospeech
from moviepy.editor import (
    AudioFileClip,
    ColorClip,
    CompositeVideoClip,
    ImageClip,
    TextClip,
    concatenate_videoclips,
    CompositeAudioClip,
    afx,
    VideoFileClip,
    vfx,
    audio_normalize,
    concatenate_audioclips,
)
from moviepy.video.fx.all import zoom_in
from moviepy.editor import (
    AudioFileClip,
    ColorClip,
    CompositeVideoClip,
    ImageClip,
    TextClip,
    concatenate_videoclips,
    CompositeAudioClip,
    afx,
    VideoFileClip,
    vfx,
    audio_normalize,
    concatenate_audioclips,
)
from moviepy.video.fx.all import zoom_in

assets = {
    "images": {
        "scene1": {"path": "/caminho/para/imagem1.jpg", "text": "Texto da cena 1"},
        "scene2": {"path": "/caminho/para/imagem2.jpg", "text": "Texto da cena 2"},
    },
    "temp_dir": "/caminho/para/temp",
    "background_music_path": "/caminho/para/musica_de_fundo.mp3",
}

logger = logging.getLogger(__name__)


class VideoRendererService:
    """
    Renderiza o vídeo final combinando assets (vídeos, áudio, texto).
    """

    def __init__(self):
        """Inicializa o serviço e o cliente de Text-to-Speech."""
        self._tts_client: Optional[texttospeech.TextToSpeechClient] = None
        logger.info("VideoRendererService initialized with lazy TTS client.")

    @property
    def tts_client(self) -> Optional[texttospeech.TextToSpeechClient]:
        """Lazy initialize TTS client."""
        if self._tts_client is None:
            try:
                self._tts_client = texttospeech.TextToSpeechClient()
                logger.info(
                    "Cliente Google Cloud Text-to-Speech inicializado com sucesso."
                )
            except Exception as e:
                logger.error(
                    f"Falha ao inicializar o cliente Text-to-Speech: {e}", exc_info=True
                )
        return self._tts_client

    async def render_video(
        self,
        script_data: Dict[str, Any],
        assets: Dict[str, Any],
        output_path: str,
        voice_name: str,
        aspect_ratio: str = "16:9",
        resolution: str = "1080p",
    ) -> str:
        """
        Orquestra a renderização do vídeo.

        Args:
            script_data: Dados do roteiro (título, texto completo).
            assets: Dicionário com os caminhos para os vídeos de cada cena.
            output_path: Caminho onde o vídeo final será salvo.
            voice_name: O nome da voz a ser usada para a narração (ex: "pt-BR-Wavenet-B").
            aspect_ratio: A proporção do vídeo ('16:9', '9:16', '1:1').
            resolution: A resolução do vídeo ('720p', '1080p', '4k').

        Returns:
            O caminho para o vídeo renderizado.
        """
        # Define as dimensões do vídeo com base na proporção e resolução
        resolutions = {
            "16:9": {"720p": (1280, 720), "1080p": (1920, 1080), "4k": (3840, 2160)},
            "9:16": {"720p": (720, 1280), "1080p": (1080, 1920), "4k": (2160, 3840)},
            "1:1": {"720p": (720, 720), "1080p": (1080, 1080), "4k": (2160, 2160)},
        }
        if (
            aspect_ratio not in resolutions
            or resolution not in resolutions[aspect_ratio]
        ):
            raise ValueError("Proporção ou resolução inválida.")

        target_size = resolutions[aspect_ratio][resolution]
        logger.info(
            f"Renderizando vídeo em {resolution} com proporção {aspect_ratio} ({target_size[0]}x{target_size[1]})"
        )

        loop = asyncio.get_event_loop()
        temp_dir = assets.get("temp_dir", os.path.dirname(output_path))

        # Carrega clipes de introdução e encerramento, se fornecidos
        intro_clip_path = assets.get("intro_clip_path")
        outro_clip_path = assets.get("outro_clip_path")

        background_music_path = assets.get("background_music_path")

        # 1. Gerar narração
        full_script_text = script_data.get("script", "")

        # Cache Inteligente: Gera um nome de arquivo baseado no hash do roteiro e da voz
        script_hash = hashlib.md5((full_script_text + voice_name).encode()).hexdigest()
        cached_narration_path = os.path.join(temp_dir, f"narration_{script_hash}.mp3")

        if not os.path.exists(cached_narration_path):
            await self._generate_narration(
                full_script_text, cached_narration_path, voice_name
            )
        else:
            logger.info(f"Usando narração em cache: {cached_narration_path}")

        narration_audio = AudioFileClip(cached_narration_path)
        total_duration = narration_audio.duration

        # Carrega a música de fundo, se fornecida, e ajusta a duração
        if background_music_path:
            background_music = AudioFileClip(background_music_path).subclip(
                0, total_duration
            )

            # Reduz o volume da música de fundo para não sobrepor a narração
            background_music = background_music.volumex(
                0.3
            )  # Ajuste este valor conforme necessário

            # Combina a narração com a música de fundo
            final_audio = CompositeAudioClip([narration_audio, background_music])
        else:
            final_audio = narration_audio

        # Normaliza o áudio final para um volume consistente
        final_audio = final_audio.fx(audio_normalize)

        # Assume que o script_data agora contém um roteiro estruturado
        # Ex: {"title": "Título SEO", "script": "...", "scenes": [{"text": "..."}, ...]}
        structured_script = script_data.get("scenes", [])

        # 2. Criar clipes de vídeo para cada cena
        video_scenes = assets.get(
            "scenes", {}
        )  # Alterado de "images" para "scenes" para ser mais genérico
        num_scenes = len(video_scenes)
        if num_scenes == 0:
            raise ValueError("Nenhum asset de vídeo fornecido para renderização.")

        duration_per_scene = total_duration / num_scenes
        final_clips = []
        transition_duration = 1  # Duração da transição em segundos

        for i, (scene_key, scene_data) in enumerate(video_scenes.items()):
            asset_path = scene_data.get("path")
            scene_text = (
                structured_script[i]["text"] if i < len(structured_script) else ""
            )
            clip = None
            ken_burns_effect = scene_data.get("ken_burns", {})

            # Verifica se o asset é um vídeo ou uma imagem
            if asset_path.lower().endswith((".mp4", ".mov", ".avi")):
                # É um clipe de vídeo
                video_clip = VideoFileClip(asset_path)
                # Ajusta a duração do clipe de vídeo para a duração da cena
                # Redimensiona e corta para o formato de destino
                if video_clip.duration > duration_per_scene:
                    clip = video_clip.subclip(0, duration_per_scene)
                else:
                    # Faz o vídeo repetir caso seja mais curto que a cena
                    clip = video_clip.fx(vfx.loop, duration=duration_per_scene)
            else:
                # É uma imagem estática
                img_clip = ImageClip(asset_path).set_duration(duration_per_scene)

                # Efeito Ken Burns Avançado
                zoom_direction = ken_burns_effect.get("zoom_direction", "in")
                zoom_amount = ken_burns_effect.get("zoom_amount", 1.15)

                def resize_func(t):
                    if zoom_direction == "in":
                        return 1 + (zoom_amount - 1) * (t / duration_per_scene)
                    else:  # zoom out
                        return zoom_amount - (zoom_amount - 1) * (
                            t / duration_per_scene
                        )

                clip = img_clip.resize(resize_func)

            # Garante que todos os clipes tenham o tamanho e a proporção corretos
            clip = clip.resize(
                width=target_size[0] if aspect_ratio != "9:16" else None,
                height=target_size[1] if aspect_ratio == "9:16" else None,
            )
            clip = clip.crop(
                x_center=clip.w / 2,
                y_center=clip.h / 2,
                width=target_size[0],
                height=target_size[1],
            )

            # Adiciona o texto sobre o vídeo
            clip_w, _ = target_size
            txt_clip = (
                TextClip(
                    scene_text,
                    fontsize=70,
                    color="white",
                    font="Arial-Bold",
                    stroke_color="black",
                    stroke_width=2,
                    method="caption",
                    size=(clip_w * 0.9, None),
                )
                .set_position(("center", "bottom"))
                .set_duration(duration_per_scene)
                .fadein(0.5)
                .fadeout(0.5)
            )

            # Compõe o vídeo com o texto
            video_with_text = CompositeVideoClip([clip, txt_clip])
            final_clips.append(video_with_text)

        # 2.5. Criar Cartão de Título (SEO)
        seo_title = script_data.get("title", "Vídeo Gerado por IA")
        title_card = (
            TextClip(
                seo_title,
                fontsize=90,
                color="white",
                font="Arial-Bold",
                method="caption",
                size=(target_size[0] * 0.9, None),
            )
            .set_position("center")
            .set_duration(3)  # Duração do cartão de título
            .fadein(0.5)
            .fadeout(0.5)
        )

        background_title = ColorClip(size=target_size, color=(0, 0, 0), duration=3)
        title_video_part = CompositeVideoClip([background_title, title_card])
        # 3. Concatena clipes de cena com transições
        main_content_video = None
        if len(final_clips) > 1:
            # Aplica um crossfade de entrada em todos os clipes, exceto o primeiro
            clips_with_transition = [final_clips[0]] + [
                clip.fx(crossfadein, transition_duration) for clip in final_clips[1:]
            ]
            main_content_video = concatenate_videoclips(
                clips_with_transition, padding=-transition_duration, method="compose"
            )
        elif final_clips:
            main_content_video = final_clips[0]

        # Adiciona clipes de introdução e encerramento
        all_video_parts = []
        all_audio_parts = []

        # Adiciona o cartão de título no início
        all_video_parts.append(title_video_part)

        if intro_clip_path and main_content_video:
            intro_clip = VideoFileClip(intro_clip_path).resize(target_size)
            all_video_parts.append(intro_clip)
            if intro_clip.audio:
                all_audio_parts.append(intro_clip.audio)

        if main_content_video:
            all_video_parts.append(main_content_video)
            all_audio_parts.append(final_audio)

        if outro_clip_path and main_content_video:
            outro_clip = VideoFileClip(outro_clip_path).resize(target_size)
            all_video_parts.append(outro_clip)
            if outro_clip.audio:
                all_audio_parts.append(outro_clip.audio)

        if not all_video_parts:
            raise ValueError("Nenhum conteúdo de vídeo para renderizar.")

        final_video = concatenate_videoclips(all_video_parts, method="compose")
        final_audio_full = concatenate_audioclips(all_audio_parts)
        # Adiciona a marca d'água (watermark) se fornecida
        watermark_path = assets.get("watermark_path")
        if watermark_path:
            logger.info(f"Adicionando marca d'água de: {watermark_path}")
            watermark_clip = (
                ImageClip(watermark_path)
                .set_duration(final_video.duration)
                .resize(height=50)  # Ajuste o tamanho conforme necessário
                .margin(right=8, top=8, opacity=0)  # Adiciona margem
                .set_pos(("right", "top"))
                .set_opacity(0.75)
            )  # Ajusta a opacidade

            final_video = CompositeVideoClip([final_video, watermark_clip])

        # 4. Adiciona a narração
        final_video = final_video.set_audio(final_audio_full)

        # 4.5. Gerar e logar capítulos do YouTube
        youtube_chapters = self._generate_youtube_chapters(
            script_data, final_video.duration
        )
        logger.info("Capítulos do YouTube Gerados:")
        for chapter in youtube_chapters:
            logger.info(f"- {chapter}")
        # 5. Renderiza o arquivo final
        logger.info(f"Renderizando vídeo final em: {output_path}")
        await loop.run_in_executor(
            None,
            lambda: final_video.write_videofile(
                output_path,
                codec="libx264",
                audio_codec="aac",
                temp_audiofile=os.path.join(temp_dir, "temp-audio.m4a"),
                remove_temp=True,
                fps=24,
                logger=None,  # Desativa o logger verboso do moviepy
                threads=os.cpu_count(),  # Otimização: usa todos os cores de CPU disponíveis
            ),
        )

        logger.info("Renderização do vídeo concluída.")
        return output_path

    async def _generate_narration(self, text: str, output_path: str, voice_name: str):
        """Gera um arquivo de áudio a partir do texto usando a API Google Cloud Text-to-Speech."""
        if not self.tts_client:
            raise ConnectionError("Cliente Text-to-Speech não inicializado.")

        logger.info(f"Gerando narração com a voz '{voice_name}' para: {output_path}")

        synthesis_input = texttospeech.SynthesisInput(text=text)

        # Extrai o código do idioma do nome da voz (ex: "pt-BR")
        language_code = "-".join(voice_name.split("-")[:2])

        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code, name=voice_name
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        response = self.tts_client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        with open(output_path, "wb") as out:
            out.write(response.audio_content)
            logger.info(f"Narração salva em {output_path}")

    def _generate_youtube_chapters(
        self, script_data: Dict[str, Any], total_duration: float
    ) -> list[str]:
        """
        Gera uma lista de strings de capítulos para a descrição do YouTube.
        """
        chapters = []
        scenes = script_data.get("scenes", [])
        if not scenes:
            return []

        # A duração do cartão de título é adicionada ao início
        title_card_duration = 3.0
        duration_per_scene = (total_duration - title_card_duration) / len(scenes)
        current_timestamp = title_card_duration

        # Capítulo de introdução
        chapters.append("00:00 - Introdução")

        for i, scene in enumerate(scenes):
            minutes, seconds = divmod(int(current_timestamp), 60)
            timestamp_str = f"{minutes:02d}:{seconds:02d}"

            # Usa o início do texto da cena como título do capítulo
            chapter_title = scene.get("text", f"Cena {i+1}").split(".")[0]
            chapters.append(f"{timestamp_str} - {chapter_title}")

            current_timestamp += duration_per_scene

        return chapters
