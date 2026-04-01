package com.example.speechtospeech

import android.content.Context
import android.os.Bundle
import android.speech.tts.TextToSpeech
import android.util.Log
import com.google.gson.Gson
import com.google.mlkit.nl.translate.*
import kotlinx.coroutines.*
import org.vosk.Model
import org.vosk.Recognizer
import java.io.File
import java.util.*

class TranslationManager(private val context: Context) {

    private var model: Model? = null
    private var recognizer: Recognizer? = null
    private var tts: TextToSpeech? = null
    private var translator: Translator? = null

    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    private val sampleRate = 16000.0f

    init {
        initTTS()
        initTranslator()
    }

    // ---------------------------
    // INIT VOSK (with asset copy)
    // ---------------------------
    fun initSTT(modelPath: String) {
        try {
            val modelDir = File(modelPath)
            model = Model(modelDir.absolutePath)
            recognizer = Recognizer(model, sampleRate)
        } catch (e: Exception) {
            Log.e("TM", "Vosk init error: ${e.message}")
        }
    }

    // ---------------------------
    // INIT ML KIT TRANSLATOR
    // ---------------------------
    private fun initTranslator() {
        val options = TranslatorOptions.Builder()
            .setSourceLanguage(TranslateLanguage.HINDI)
            .setTargetLanguage(TranslateLanguage.BENGALI)
            .build()

        translator = Translation.getClient(options)

        translator?.downloadModelIfNeeded()
            ?.addOnSuccessListener {
                Log.d("TM", "Translation model ready")
            }
            ?.addOnFailureListener {
                Log.e("TM", "Model download failed: ${it.message}")
            }
    }

    // ---------------------------
    // INIT TTS
    // ---------------------------
    private fun initTTS() {
        tts = TextToSpeech(context) { status ->
            if (status == TextToSpeech.SUCCESS) {
                val result = tts?.setLanguage(Locale("bn", "IN"))
                if (result == TextToSpeech.LANG_NOT_SUPPORTED) {
                    tts?.setLanguage(Locale.ENGLISH) // fallback
                }
            }
        }
    }

    // ---------------------------
    // PROCESS AUDIO (REAL-TIME)
    // ---------------------------
    fun processAudio(data: ByteArray, length: Int, onResult: (String) -> Unit) {
        val rec = recognizer ?: return

        if (rec.acceptWaveForm(data, length)) {
            val text = extractText(rec.result)
            if (text.isNotEmpty()) onResult(text)
        } else {
            val partial = extractText(rec.partialResult)
            if (partial.isNotEmpty()) onResult(partial)
        }
    }

    // ---------------------------
    // JSON PARSER (SAFE)
    // ---------------------------
    data class VoskResult(val text: String = "", val partial: String = "")

    private fun extractText(json: String): String {
        return try {
            val res = Gson().fromJson(json, VoskResult::class.java)
            res.text.ifEmpty { res.partial }
        } catch (e: Exception) {
            ""
        }
    }

    // ---------------------------
    // TRANSLATE + SPEAK (ASYNC)
    // ---------------------------
    fun translateAndSpeak(input: String, onTranslated: (String) -> Unit) {
        val trans = translator ?: return

        scope.launch {
            try {
                trans.translate(input)
                    .addOnSuccessListener { translated ->
                        onTranslated(translated)
                        speak(translated)
                    }
                    .addOnFailureListener {
                        Log.e("TM", "Translation failed")
                    }
            } catch (e: Exception) {
                Log.e("TM", "Error: ${e.message}")
            }
        }
    }

    // ---------------------------
    // SPEAK
    // ---------------------------
    private fun speak(text: String) {
        val bundle = Bundle().apply {
            putFloat(TextToSpeech.Engine.KEY_PARAM_VOLUME, 1.0f)
        }
        tts?.speak(text, TextToSpeech.QUEUE_FLUSH, bundle, "tts1")
    }

    // ---------------------------
    // CLEANUP
    // ---------------------------
    fun shutdown() {
        scope.cancel()
        recognizer?.close()
        model?.close()
        translator?.close()
        tts?.shutdown()
    }
}
