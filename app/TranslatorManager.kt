package com.example.offlinetranslator

import android.Manifest
import android.content.pm.PackageManager
import android.media.*
import android.os.Bundle
import android.speech.tts.TextToSpeech
import android.widget.LinearLayout
import android.widget.TextView
import androidx.activity.ComponentActivity
import androidx.core.app.ActivityCompat
import androidx.lifecycle.lifecycleScope
import com.google.gson.Gson
import com.google.mlkit.nl.translate.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.tasks.await
import kotlinx.coroutines.withContext
import org.vosk.Model
import org.vosk.Recognizer
import java.io.File
import java.io.FileOutputStream
import java.util.*

class MainActivity : ComponentActivity() {

    // ---------------------------
    // CORE
    // ---------------------------
    private var model: Model? = null
    private var recognizer: Recognizer? = null
    private var translator: Translator? = null
    private var tts: TextToSpeech? = null

    private val gson = Gson()
    private val sampleRate = 16000.0f

    private lateinit var spokenView: TextView
    private lateinit var translatedView: TextView

    private var isRecording = true
    private var lastSentence = ""

    // ---------------------------
    // ON CREATE
    // ---------------------------
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // UI
        spokenView = TextView(this)
        translatedView = TextView(this)

        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            addView(spokenView)
            addView(translatedView)
        }

        setContentView(layout)

        // Permissions
        ActivityCompat.requestPermissions(
            this,
            arrayOf(Manifest.permission.RECORD_AUDIO),
            1
        )

        initAll()
    }

    // ---------------------------
    // INIT EVERYTHING
    // ---------------------------
    private fun initAll() {
        lifecycleScope.launch(Dispatchers.IO) {

            copyModelIfNeeded()

            initSTT()
            initTranslator()
            initTTS()

            startMic()
        }
    }

    // ---------------------------
    // VOSK INIT
    // ---------------------------
    private fun initSTT() {
        val modelPath = File(filesDir, "vosk-model").absolutePath
        model = Model(modelPath)
        recognizer = Recognizer(model, sampleRate)
    }

    // ---------------------------
    // TRANSLATOR INIT (OFFLINE)
    // ---------------------------
    private fun initTranslator() {
        val options = TranslatorOptions.Builder()
            .setSourceLanguage(TranslateLanguage.HINDI)
            .setTargetLanguage(TranslateLanguage.BENGALI)
            .build()

        translator = Translation.getClient(options)
    }

    // ---------------------------
    // TTS INIT
    // ---------------------------
    private fun initTTS() {
        tts = TextToSpeech(this) {
            tts?.setLanguage(Locale("bn", "IN"))
        }
    }

    // ---------------------------
    // MIC LOOP
    // ---------------------------
    private fun startMic() {
        val bufferSize = AudioRecord.getMinBufferSize(
            16000,
            AudioFormat.CHANNEL_IN_MONO,
            AudioFormat.ENCODING_PCM_16BIT
        )

        val recorder = AudioRecord(
            MediaRecorder.AudioSource.MIC,
            16000,
            AudioFormat.CHANNEL_IN_MONO,
            AudioFormat.ENCODING_PCM_16BIT,
            bufferSize
        )

        recorder.startRecording()

        val buffer = ByteArray(bufferSize)

        while (isRecording) {
            val read = recorder.read(buffer, 0, buffer.size)
            if (read > 0) {
                processAudio(buffer, read)
            }
        }
    }

    // ---------------------------
    // PROCESS AUDIO
    // ---------------------------
    private fun processAudio(data: ByteArray, length: Int) {
        val rec = recognizer ?: return

        val json = if (rec.acceptWaveForm(data, length)) {
            rec.result
        } else {
            rec.partialResult
        }

        val text = extractText(json)

        if (text.isNotEmpty()) {
            runOnUiThread {
                spokenView.text = "🎤 $text"
            }

            if (shouldTranslate(text)) {
                lastSentence = text

                lifecycleScope.launch {
                    val translated = translate(text)
                    translated?.let {
                        runOnUiThread {
                            translatedView.text = "🌐 $it"
                        }
                        speak(it)
                    }
                }
            }
        }
    }

    // ---------------------------
    // JSON PARSE
    // ---------------------------
    private fun extractText(json: String): String {
        return try {
            val res = gson.fromJson(json, VoskResult::class.java)
            res.text.ifEmpty { res.partial }
        } catch (e: Exception) {
            ""
        }
    }

    data class VoskResult(val text: String = "", val partial: String = "")

    // ---------------------------
    // TRANSLATE
    // ---------------------------
    private suspend fun translate(text: String): String? {
        return try {
            translator?.translate(text)?.await()
        } catch (e: Exception) {
            null
        }
    }

    // ---------------------------
    // SPEAK
    // ---------------------------
    private suspend fun speak(text: String) {
        withContext(Dispatchers.Main) {
            tts?.speak(text, TextToSpeech.QUEUE_FLUSH, null, "tts1")
        }
    }

    // ---------------------------
    // SENTENCE DETECTION
    // ---------------------------
    private fun shouldTranslate(text: String): Boolean {
        return text.length > 8 &&
                text != lastSentence &&
                (text.endsWith(".") || text.endsWith("।"))
    }

    // ---------------------------
    // COPY MODEL FROM ASSETS
    // ---------------------------
    private fun copyModelIfNeeded() {
        val dir = File(filesDir, "vosk-model")
        if (dir.exists()) return

        dir.mkdirs()
        assets.list("vosk-model")?.forEach { file ->
            val input = assets.open("vosk-model/$file")
            val outFile = File(dir, file)
            val output = FileOutputStream(outFile)

            input.copyTo(output)
            input.close()
            output.close()
        }
    }

    // ---------------------------
    // CLEANUP
    // ---------------------------
    override fun onDestroy() {
        super.onDestroy()
        isRecording = false
        recognizer?.close()
        model?.close()
        translator?.close()
        tts?.shutdown()
    }
}
