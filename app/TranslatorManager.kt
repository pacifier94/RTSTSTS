package com.example.speechtospeech

import android.content.Context
import android.speech.tts.TextToSpeech
import android.util.Log
import org.vosk.Model
import org.vosk.Recognizer
import java.io.IOException
import java.util.Locale

class TranslationManager(private val context: Context) {

    private var model: Model? = null
    private var recognizer: Recognizer? = null
    private var tts: TextToSpeech? = null

    private val sampleRate = 16000.0f

    init {
        initTTS()
    }

    // ---------------------------
    // Initialize Vosk Model
    // ---------------------------
    fun initSTT(modelPath: String) {
        try {
            model = Model(modelPath)
            recognizer = Recognizer(model, sampleRate)
        } catch (e: IOException) {
            Log.e("TranslationManager", "Error initializing Vosk model: ${e.message}")
        }
    }

    // ---------------------------
    // Initialize Text-to-Speech
    // ---------------------------
    private fun initTTS() {
        tts = TextToSpeech(context) { status ->
            if (status == TextToSpeech.SUCCESS) {
                // Bengali output
                val result = tts?.setLanguage(Locale("bn", "IN"))
                if (result == TextToSpeech.LANG_MISSING_DATA ||
                    result == TextToSpeech.LANG_NOT_SUPPORTED
                ) {
                    Log.e("TranslationManager", "Bengali TTS not supported")
                }
            } else {
                Log.e("TranslationManager", "TTS Initialization failed")
            }
        }
    }

    // ---------------------------
    // Process Audio Input (Vosk)
    // ---------------------------
    fun processAudio(data: ByteArray, length: Int): String? {
        recognizer?.let {
            return if (it.acceptWaveForm(data, length)) {
                val result = it.result
                extractText(result)
            } else {
                null
            }
        }
        return null
    }

    // ---------------------------
    // Extract text from Vosk JSON
    // ---------------------------
    private fun extractText(json: String): String {
        // Simple parsing (better use Gson in production)
        return try {
            val regex = """"text"\s*:\s*"([^"]*)"""".toRegex()
            regex.find(json)?.groups?.get(1)?.value ?: ""
        } catch (e: Exception) {
            ""
        }
    }

    // ---------------------------
    // Translate Hindi → Bengali
    // ---------------------------
    fun translateHindiToBengali(input: String): String {
        // Placeholder logic
        // Replace with ML Kit / API later

        val dictionary = mapOf(
            "नमस्ते" to "নমস্কার",
            "आप कैसे हैं" to "আপনি কেমন আছেন",
            "धन्यवाद" to "ধন্যবাদ"
        )

        return dictionary[input] ?: "[अनुवाद उपलब्ध नहीं]"
    }

    // ---------------------------
    // Speak Output
    // ---------------------------
    fun speak(text: String) {
        tts?.speak(text, TextToSpeech.QUEUE_FLUSH, null, null)
    }

    // ---------------------------
    // Full Pipeline
    // ---------------------------
    fun handleSpeechInput(audioData: ByteArray, length: Int) {
        val hindiText = processAudio(audioData, length)

        hindiText?.let {
            Log.d("TranslationManager", "Recognized Hindi: $it")

            val bengaliText = translateHindiToBengali(it)
            Log.d("TranslationManager", "Translated Bengali: $bengaliText")

            speak(bengaliText)
        }
    }

    // ---------------------------
    // Cleanup
    // ---------------------------
    fun shutdown() {
        recognizer?.close()
        model?.close()
        tts?.shutdown()
    }
}
