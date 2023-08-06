from .Functions import is_flatpak
import subprocess


class FFmpegHandler:
    def __init__(self, env) -> None:
        self._env = env

    def get_ffmpeg_command(self) -> str:
        if is_flatpak():
            return "/app/bin/ffmpeg"
        elif self._env.settings.get("useCustomFFmpegPath"):
            return self._env.settings.get("customFFmpegPath")
        else:
            return "ffmpeg"

    def execute_ffmpeg_command(self, arguments: list[str]) -> subprocess.CompletedProcess:
        return subprocess.run([self.get_ffmpeg_command()] + arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def is_ffmpeg_installed(self) -> bool:
        try:
            result = subprocess.run(self.get_ffmpeg_command(), stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            return result.stderr.startswith(b"ffmpeg")
        except Exception:
            return False
