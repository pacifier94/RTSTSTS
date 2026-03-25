package com.example.translator1

import android.content.Context
import android.util.Log
import ai.onnxruntime.*
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import java.io.File
import java.io.FileOutputStream
import java.io.InputStreamReader
import java.nio.LongBuffer

class TranslatorManager(
    private val context: Context,
    private val modelDirName: String
) {

    private val env: OrtEnvironment = OrtEnvironment.getEnvironment()
    private val encoderSession: OrtSession
    private val decoderSession: OrtSession

    private val vocab: Map<String, Int>
    private val idToPiece: Map<Int, String>

    init {
        val modelDir = copyAssetFolder(modelDirName)

        encoderSession = env.createSession(File(modelDir, "encoder_model.onnx").absolutePath)
        decoderSession = env.createSession(File(modelDir, "decoder_model.onnx").absolutePath)

        val vocabFile = File(modelDir, "vocab.json")
        vocab = loadVocab(vocabFile)
        idToPiece = vocab.entries.associate { it.value to it.key }

        Log.d("TRANSLATOR", "$modelDirName model loaded (${vocab.size} tokens)")
    }

    fun translate(text: String): String {
        Log.d("TRANSLATOR", "Input ($modelDirName): $text")

        val inputIds = encode(text)

        val (encoderHidden, encoderMask) = runEncoder(inputIds)

        val outputTokens = runDecoder(encoderHidden, encoderMask)

        val result = decode(outputTokens)

        Log.d("TRANSLATOR", "Output ($modelDirName): $result")

        encoderHidden.close()
        encoderMask.close()

        return result
    }

    // ====================== Encode ======================
    private fun encode(text: String): LongArray {

        val normalized = text.trim()

        val ids = mutableListOf<Long>()
        ids.add(0L) // BOS

        // Try full sentence lookup first
        if (vocab.containsKey(normalized)) {
            ids.add(vocab[normalized]!!.toLong())
        } else {
            // fallback: character-level (better than broken regex)
            for (ch in normalized) {
                val piece = ch.toString()
                ids.add(vocab[piece]?.toLong() ?: vocab.getOrDefault("<unk>", 3).toLong())
            }
        }

        ids.add(2L) // EOS

        return ids.toLongArray()
    }

    // ====================== Decode ======================
    private fun decode(tokens: List<Int>): String {
        val pieces = tokens.mapNotNull { idToPiece[it] }
            .filter { it != "</s>" && it != "<s>" && it != "<pad>" }

        return pieces.joinToString(" ")
            .replace("▁", " ")
            .trim()
    }

    private fun loadVocab(vocabFile: File): Map<String, Int> {
        val gson = Gson()
        val type = object : TypeToken<Map<String, Int>>() {}.type
        InputStreamReader(vocabFile.inputStream()).use { reader ->
            return gson.fromJson(reader, type)
        }
    }

    // ====================== Encoder ======================
    private fun runEncoder(inputIds: LongArray): Pair<OnnxTensor, OnnxTensor> {
        val seqLen = inputIds.size.toLong()
        val shape = longArrayOf(1L, seqLen)

        val attentionMask = LongArray(inputIds.size) { 1L }

        val inputTensor = OnnxTensor.createTensor(env, LongBuffer.wrap(inputIds), shape)
        val maskTensor = OnnxTensor.createTensor(env, LongBuffer.wrap(attentionMask), shape)

        val inputs = mapOf(
            "input_ids" to inputTensor,
            "attention_mask" to maskTensor
        )

        val result = encoderSession.run(inputs)

        @Suppress("UNCHECKED_CAST")
        val hiddenStates = result[0].value as Array<Array<FloatArray>>

        inputTensor.close()
        result.close()

        val hiddenTensor = OnnxTensor.createTensor(env, hiddenStates)

        return Pair(hiddenTensor, maskTensor)
    }

    // ====================== Decoder ======================
    private fun runDecoder(
        encoderHidden: OnnxTensor,
        encoderMask: OnnxTensor
    ): List<Int> {

        val tokens = mutableListOf<Int>()
        var decoderInput = intArrayOf(0) // BOS
        val MAX_LENGTH = 120

        for (i in 0 until MAX_LENGTH) {

            val shape = longArrayOf(1L, decoderInput.size.toLong())

            val decoderTensor = OnnxTensor.createTensor(
                env,
                LongBuffer.wrap(decoderInput.map { it.toLong() }.toLongArray()),
                shape
            )

            val inputs = mapOf(
                "input_ids" to decoderTensor,
                "encoder_hidden_states" to encoderHidden,
                "encoder_attention_mask" to encoderMask // ✅ FIX
            )

            val output = decoderSession.run(inputs)

            @Suppress("UNCHECKED_CAST")
            val logits = output[0].value as Array<Array<FloatArray>>

            val lastLogits = logits[0][decoderInput.size - 1]

            val nextToken = argmax(lastLogits)

            decoderTensor.close()
            output.close()

            if (nextToken == 2) break

            tokens.add(nextToken)
            decoderInput += nextToken
        }

        return tokens
    }

    private fun argmax(array: FloatArray): Int {
        var maxIndex = 0
        var maxValue = array[0]

        for (i in 1 until array.size) {
            if (array[i] > maxValue) {
                maxValue = array[i]
                maxIndex = i
            }
        }
        return maxIndex
    }

    // ====================== Asset Copy ======================
    private fun copyAssetFolder(assetPath: String): File {
        val dest = File(context.filesDir, assetPath)
        if (!dest.exists()) {
            dest.mkdirs()
            copyAssets(assetPath, dest)
        }
        return dest
    }

    private fun copyAssets(assetFolder: String, dest: File) {
        val files = context.assets.list(assetFolder) ?: return
        if (!dest.exists()) dest.mkdirs()

        for (fileName in files) {
            val path = "$assetFolder/$fileName"
            val outFile = File(dest, fileName)

            if (context.assets.list(path)?.isNotEmpty() == true) {
                copyAssets(path, outFile)
            } else {
                context.assets.open(path).use { input ->
                    FileOutputStream(outFile).use { output ->
                        input.copyTo(output)
                    }
                }
            }
        }
    }
}