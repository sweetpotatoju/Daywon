import textwrap
import os
from gtts import gTTS
from moviepy.editor import ImageClip, concatenate_videoclips, CompositeVideoClip, TextClip, AudioFileClip
# https://www.imagemagick.org/script/download.php#windows에서 imagemagick(dynamic ver) 다운
# -> (+) 레거시 추가 체크 후, 설치 (pip 설치 불가능)


class VideoCreator:
    def __init__(self, clips_info):
        self.clips_info = clips_info
        self.video_name = 'completed_video'
        self.font = 'NanumGothic'
        self.fontsize = 60
        self.color = 'black'
        self.wrap_width = 20
        self.padding = 20
        self.audio_folder = './audio'
        self.video_folder = './completed_video'
        self.ensure_folders_exists()
        self.output_path = self.create_video_file_name()

    def ensure_folders_exists(self):
        # 오디오 폴더와 비디오 폴더가 있는지 확인하고 없다면 생성
        os.makedirs(self.audio_folder, exist_ok=True)
        os.makedirs(self.video_folder, exist_ok=True)

    def create_video_file_name(self):
        """저장할 비디오 파일의 이름을 중복되지 않게 생성"""
        count = 1
        while True:
            video_path = f"./{self.video_folder}/{self.video_name}_{count}.mp4"
            if not os.path.exists(video_path):
                return video_path
            count += 1

    def create_video(self):
        clips = []
        for path, text in self.clips_info:
            # 긴 텍스트를 적절한 길이로 줄바꿈
            wrapped_text = textwrap.fill(text, width=self.wrap_width)

            # TTS를 사용하여 오디오 파일 생성
            tts = gTTS(text=wrapped_text, lang='ko')
            audio_filename = f'{self.audio_folder}/{os.path.basename(path).split(".")[0]}.mp3'
            tts.save(audio_filename)

            # 오디오 클립 생성 및 지속시간 확인
            audio_clip = AudioFileClip(audio_filename)
            duration = audio_clip.duration

            # 이미지 클립과 자막 생성
            clip = ImageClip(path, duration=duration)
            img_width, img_height = clip.size
            txt_clip = TextClip(wrapped_text, fontsize=self.fontsize, color=self.color, font=self.font, method='label')
            txt_clip = txt_clip.set_position((self.padding, 'center')).set_position(('center', 'bottom')).set_duration(
                duration)

            # 이미지와 자막을 합성하여 비디오 클립 생성
            video = CompositeVideoClip([clip, txt_clip]).set_audio(audio_clip)
            clips.append(video)

        # 모든 클립 연결
        final_clip = concatenate_videoclips(clips, method="compose")

        # 최종 비디오 파일 생성
        final_clip.write_videofile(self.output_path, fps=30, codec='libx264', audio_codec='aac')
