package com.example.translator1

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import android.util.Log
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat

import org.vosk.Model
import org.vosk.Recognizer
import org.vosk.android.SpeechService
import org.vosk.android.RecognitionListener

import java.io.File
import java.io.FileOutputStream

import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform

class MainActivity : AppCompatActivity(), RecognitionListener {

    private lateinit var buttonSpeak: Button
    private lateinit var textViewInput: TextView
    private lateinit var textViewOutput: TextView

    private var model: Model? = null
    private var recognizer: Recognizer? = null
    private var speechService: SpeechService? = null

    private val RECORD_AUDIO_REQUEST_CODE = 101

    override fun onCreate(savedInstanceState: Bundle?) {

        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        buttonSpeak = findViewById(R.id.buttonSpeak)
        textViewInput = findViewById(R.id.textViewInput)
        textViewOutput = findViewById(R.id.textViewOutput)

        buttonSpeak.isEnabled = false

        // Start Python
        if (!Python.isStarted()) {
            Python.start(AndroidPlatform(this))
        }

        // Ask microphone permission
        if (ContextCompat.checkSelfPermission(
                this,
                Manifest.permission.RECORD_AUDIO
            ) != PackageManager.PERMISSION_GRANTED
        ) {

            ActivityCompat.requestPermissions(
                this,
                arrayOf(Manifest.permission.RECORD_AUDIO),
                RECORD_AUDIO_REQUEST_CODE
            )

        } else {
            initializeVoskModel()
        }

        buttonSpeak.setOnClickListener {

            textViewInput.text = ""
            textViewOutput.text = ""

            startRecognition()

            Toast.makeText(this, "Speak Hindi", Toast.LENGTH_SHORT).show()
        }
    }

    // Copy assets
    private fun copyAssetFolder(assetFolder: String, destFolder: File) {

        val files = assets.list(assetFolder) ?: return

        if (!destFolder.exists()) destFolder.mkdirs()

        for (file in files) {

            val path = "$assetFolder/$file"
            val outFile = File(destFolder, file)

            if (assets.list(path)?.isNotEmpty() == true) {

                copyAssetFolder(path, outFile)

            } else {

                assets.open(path).use { input ->
                    FileOutputStream(outFile).use { output ->
                        input.copyTo(output)
                    }
                }
            }
        }
    }

    // Initialize Vosk
    private fun initializeVoskModel() {

        Thread {

            try {

                val modelDir = File(filesDir, "hindi-model")

                if (!modelDir.exists()) {
                    copyAssetFolder("hindi-model", modelDir)
                }

                model = Model(modelDir.absolutePath)
                recognizer = Recognizer(model, 16000f)

                runOnUiThread {

                    buttonSpeak.isEnabled = true

                    Toast.makeText(
                        this,
                        "Vosk Ready",
                        Toast.LENGTH_SHORT
                    ).show()
                }

            } catch (e: Exception) {
                e.printStackTrace()
            }

        }.start()
    }

    private fun startRecognition() {

        speechService?.stop()

        speechService = SpeechService(recognizer, 16000f)

        speechService?.startListening(this)
    }

    // FINAL RESULT FROM VOSK
    override fun onFinalResult(hypothesis: String?) {

        Log.d("VOSK_JSON", hypothesis ?: "")

        val hindiText = extractText(hypothesis ?: "")

        runOnUiThread {
            textViewInput.text = hindiText
        }

        // Send to Python
        Thread {

            try {

                val py = Python.getInstance()

                val module = py.getModule("translator")

                val result = module.callAttr(
                    "translate_hi_bn",
                    hindiText
                )

                val bengaliText = result.toString()

                runOnUiThread {
                    textViewOutput.text = bengaliText
                }

            } catch (e: Exception) {

                e.printStackTrace()

                runOnUiThread {
                    textViewOutput.text = "Python Error: ${e.message}"
                }
            }

        }.start()
    }

    override fun onResult(hypothesis: String?) {

        val text = extractText(hypothesis ?: "")

        runOnUiThread {
            textViewInput.text = text
        }
    }

    override fun onPartialResult(hypothesis: String?) {

        val text = extractText(hypothesis ?: "")

        runOnUiThread {
            textViewInput.text = text
        }
    }

    override fun onError(e: Exception?) {}

    override fun onTimeout() {}

    // Extract text from Vosk JSON
    private fun extractText(json: String): String {

        val textRegex = """"text"\s*:\s*"(.*?)"""".toRegex()
        val partialRegex = """"partial"\s*:\s*"(.*?)"""".toRegex()

        val textMatch = textRegex.find(json)
        if (textMatch != null) return textMatch.groupValues[1]

        val partialMatch = partialRegex.find(json)
        if (partialMatch != null) return partialMatch.groupValues[1]

        return ""
    }

    override fun onDestroy() {

        super.onDestroy()

        speechService?.stop()
        recognizer?.close()
        model?.close()
    }
}
