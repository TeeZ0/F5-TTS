from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt, QThreadPool
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from app.audio.playback import AudioPlayer
from app.models.settings import Emotion, SplitMode, SynthesisRequest, SynthesisSettings, VoiceReference
from app.services.f5_tts_service import F5TTSService, SynthesisResult
from app.services.settings_service import SettingsService
from app.ui.theme import DARK_THEME
from app.utils.paths import EXPORTS_DIR
from app.voices.library import VoiceLibrary, VoiceProfile
from app.workers.synthesis_worker import SynthesisWorker


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("F5Narrator")
        self.setMinimumSize(980, 760)
        self.setStyleSheet(DARK_THEME)

        self.settings_service = SettingsService()
        self.settings = self.settings_service.load()
        self.tts_service = F5TTSService()
        self.thread_pool = QThreadPool.globalInstance()
        self.player = AudioPlayer()
        self.voice_library = VoiceLibrary(Path(__file__).resolve().parents[2] / "voices")
        self.voice_profiles: list[VoiceProfile] = []
        self.generated_audio_path: Path | None = None

        self.voice_selector = QComboBox()
        self.reference_path = QLineEdit()
        self.reference_path.setReadOnly(True)
        self.browse_reference_button = QPushButton("Browse...")
        self.browse_reference_button.setObjectName("secondaryButton")
        self.reference_transcript = QPlainTextEdit()
        self.reference_transcript.setPlaceholderText("Transcript of the reference voice sample...")
        self.script_editor = QPlainTextEdit()
        self.script_editor.setPlaceholderText("Paste script here...")
        self.sentences_radio = QRadioButton("Sentences")
        self.paragraphs_radio = QRadioButton("Paragraphs")
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_label = QLabel()
        self.calm_radio = QRadioButton("Calm")
        self.neutral_radio = QRadioButton("Neutral")
        self.dramatic_radio = QRadioButton("Dramatic")
        self.generate_button = QPushButton("Generate")
        self.play_button = QPushButton("Play")
        self.save_button = QPushButton("Save")
        self.progress_bar = QProgressBar()
        self.status_label = QLabel("Ready")

        self._build_ui()
        self._connect_signals()
        self._load_voice_library()
        self._apply_settings()
        self._set_output_enabled(False)

    def _build_ui(self) -> None:
        central = QWidget()
        root = QVBoxLayout(central)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(14)

        title = QLabel("F5Narrator")
        title.setStyleSheet("font-size: 24pt; font-weight: 700;")
        subtitle = QLabel("Local F5-TTS narration studio for long-form voice-over production")
        subtitle.setStyleSheet("color: #8b949e;")
        root.addWidget(title)
        root.addWidget(subtitle)

        voice_group = QGroupBox("Voice")
        voice_layout = QGridLayout(voice_group)
        voice_layout.addWidget(QLabel("Voice Profile"), 0, 0)
        voice_layout.addWidget(self.voice_selector, 0, 1, 1, 2)
        voice_layout.addWidget(QLabel("Reference WAV"), 1, 0)
        voice_layout.addWidget(self.reference_path, 1, 1)
        voice_layout.addWidget(self.browse_reference_button, 1, 2)
        voice_layout.addWidget(QLabel("Transcript"), 2, 0, Qt.AlignmentFlag.AlignTop)
        voice_layout.addWidget(self.reference_transcript, 2, 1, 1, 2)
        root.addWidget(voice_group)

        script_group = QGroupBox("Script")
        script_layout = QVBoxLayout(script_group)
        script_layout.addWidget(self.script_editor)
        root.addWidget(script_group, stretch=1)

        controls_group = QGroupBox("Generation Settings")
        controls_layout = QGridLayout(controls_group)
        controls_layout.addWidget(QLabel("Split Mode"), 0, 0)
        split_layout = QHBoxLayout()
        split_layout.addWidget(self.sentences_radio)
        split_layout.addWidget(self.paragraphs_radio)
        split_layout.addStretch()
        controls_layout.addLayout(split_layout, 0, 1)

        controls_layout.addWidget(QLabel("Speaking Speed"), 1, 0)
        self.speed_slider.setRange(70, 130)
        controls_layout.addWidget(self.speed_slider, 1, 1)
        controls_layout.addWidget(self.speed_label, 1, 2)

        controls_layout.addWidget(QLabel("Emotion"), 2, 0)
        emotion_layout = QHBoxLayout()
        emotion_layout.addWidget(self.calm_radio)
        emotion_layout.addWidget(self.neutral_radio)
        emotion_layout.addWidget(self.dramatic_radio)
        emotion_layout.addStretch()
        controls_layout.addLayout(emotion_layout, 2, 1)
        root.addWidget(controls_group)

        output_group = QGroupBox("Output")
        output_layout = QVBoxLayout(output_group)
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.generate_button)
        button_layout.addWidget(self.play_button)
        button_layout.addWidget(self.save_button)
        button_layout.addStretch()
        output_layout.addLayout(button_layout)
        output_layout.addWidget(self.progress_bar)
        output_layout.addWidget(self.status_label)
        root.addWidget(output_group)
        self.setCentralWidget(central)

    def _connect_signals(self) -> None:
        self.browse_reference_button.clicked.connect(self._browse_reference)
        self.voice_selector.currentIndexChanged.connect(self._select_voice_profile)
        self.generate_button.clicked.connect(self._generate)
        self.play_button.clicked.connect(self._play)
        self.save_button.clicked.connect(self._save)
        self.speed_slider.valueChanged.connect(self._update_speed_label)

    def _load_voice_library(self) -> None:
        self.voice_selector.clear()
        self.voice_selector.addItem("Custom reference", None)
        self.voice_profiles = self.voice_library.list_voices()
        for profile in self.voice_profiles:
            self.voice_selector.addItem(profile.name, profile)

    def _apply_settings(self) -> None:
        self.sentences_radio.setChecked(self.settings.split_mode is SplitMode.SENTENCES)
        self.paragraphs_radio.setChecked(self.settings.split_mode is SplitMode.PARAGRAPHS)
        self.speed_slider.setValue(int(self.settings.speed * 100))
        self.calm_radio.setChecked(self.settings.emotion is Emotion.CALM)
        self.neutral_radio.setChecked(self.settings.emotion is Emotion.NEUTRAL)
        self.dramatic_radio.setChecked(self.settings.emotion is Emotion.DRAMATIC)
        self._update_speed_label()

    def _browse_reference(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Select reference WAV", str(Path.home()), "WAV files (*.wav)")
        if path:
            self.reference_path.setText(path)
            self.voice_selector.setCurrentIndex(0)

    def _select_voice_profile(self, index: int) -> None:
        profile = self.voice_selector.itemData(index)
        if not isinstance(profile, VoiceProfile):
            return
        self.reference_path.setText(str(profile.reference_audio))
        self.reference_transcript.setPlainText(profile.transcript.strip())

    def _generate(self) -> None:
        try:
            request = self._build_request()
        except ValueError as exc:
            QMessageBox.warning(self, "Missing input", str(exc))
            return
        self._persist_settings()
        self._set_generating(True)
        worker = SynthesisWorker(self.tts_service, request)
        worker.signals.progress.connect(self._on_progress)
        worker.signals.completed.connect(self._on_completed)
        worker.signals.failed.connect(self._on_failed)
        self.thread_pool.start(worker)

    def _build_request(self) -> SynthesisRequest:
        ref_path_text = self.reference_path.text().strip()
        if not ref_path_text:
            msg = "Choose a reference WAV before generating."
            raise ValueError(msg)
        transcript = self.reference_transcript.toPlainText().strip()
        script = self.script_editor.toPlainText().strip()
        settings = self._collect_settings()
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        output_path = EXPORTS_DIR / f"narration-{timestamp}.wav"
        return SynthesisRequest(
            voice=VoiceReference(audio_path=Path(ref_path_text), transcript=transcript),
            script=script,
            output_path=output_path,
            settings=settings,
        )

    def _collect_settings(self) -> SynthesisSettings:
        split_mode = SplitMode.PARAGRAPHS if self.paragraphs_radio.isChecked() else SplitMode.SENTENCES
        if self.calm_radio.isChecked():
            emotion = Emotion.CALM
        elif self.dramatic_radio.isChecked():
            emotion = Emotion.DRAMATIC
        else:
            emotion = Emotion.NEUTRAL
        return SynthesisSettings(
            split_mode=split_mode,
            speed=self.speed_slider.value() / 100,
            emotion=emotion,
            model_name=self.settings.model_name,
            device=self.settings.device,
            remove_silence=self.settings.remove_silence,
        )

    def _persist_settings(self) -> None:
        self.settings = self._collect_settings()
        self.settings_service.save(self.settings)

    def _set_generating(self, generating: bool) -> None:
        self.generate_button.setDisabled(generating)
        self.browse_reference_button.setDisabled(generating)
        self.progress_bar.setValue(0 if generating else self.progress_bar.value())
        if generating:
            self.status_label.setText("Starting generation...")

    def _set_output_enabled(self, enabled: bool) -> None:
        self.play_button.setEnabled(enabled)
        self.save_button.setEnabled(enabled)

    def _update_speed_label(self) -> None:
        self.speed_label.setText(f"{self.speed_slider.value() / 100:.2f}x")

    def _on_progress(self, value: int, message: str) -> None:
        self.progress_bar.setValue(value)
        self.status_label.setText(message)

    def _on_completed(self, result: object) -> None:
        synthesis_result = result
        if not isinstance(synthesis_result, SynthesisResult):
            QMessageBox.warning(self, "Generation complete", "Generation finished with an unexpected result.")
            self._set_generating(False)
            return
        self.generated_audio_path = synthesis_result.output_path
        self.player.load(synthesis_result.output_path)
        self.status_label.setText(f"Generated: {synthesis_result.output_path}")
        self.progress_bar.setValue(100)
        self._set_output_enabled(True)
        self._set_generating(False)

    def _on_failed(self, message: str, details: str) -> None:
        self._set_generating(False)
        self._set_output_enabled(False)
        self.status_label.setText("Generation failed")
        QMessageBox.critical(self, "Generation failed", f"{message}\n\nDetails:\n{details}")

    def _play(self) -> None:
        if self.generated_audio_path is None:
            return
        self.player.load(self.generated_audio_path)
        self.player.play()

    def _save(self) -> None:
        if self.generated_audio_path is None:
            return
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save narration",
            str(Path.home() / self.generated_audio_path.name),
            "WAV files (*.wav)",
        )
        if not path:
            return
        destination = Path(path)
        if destination.suffix.lower() != ".wav":
            destination = destination.with_suffix(".wav")
        shutil.copy2(self.generated_audio_path, destination)
        self.status_label.setText(f"Saved: {destination}")
