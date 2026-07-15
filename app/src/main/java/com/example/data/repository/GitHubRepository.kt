package com.example.data.repository

import android.util.Log
import com.example.BuildConfig
import com.example.data.api.GeminiApiService
import com.example.data.api.GeminiContent
import com.example.data.api.GeminiPart
import com.example.data.api.GeminiRequest
import com.example.data.api.GitHubApiService
import com.example.data.model.GitHubCommitResponse
import com.example.data.model.GitHubIssue
import com.example.data.model.GitHubRepo
import com.example.data.model.GitHubUser
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class GitHubRepository(
    private val gitHubApiService: GitHubApiService,
    private val geminiApiService: GeminiApiService
) {
    private val tag = "GitHubRepository"

    suspend fun searchRepositories(query: String, token: String?): List<GitHubRepo> = withContext(Dispatchers.IO) {
        try {
            val formattedToken = token?.let { if (it.startsWith("Bearer ") || it.startsWith("token ")) it else "token $it" }
            val response = gitHubApiService.searchRepositories(query = query, token = formattedToken)
            response.items
        } catch (e: Exception) {
            Log.e(tag, "Error searching repositories", e)
            throw e
        }
    }

    suspend fun getRepositoryDetails(owner: String, repo: String, token: String?): GitHubRepo = withContext(Dispatchers.IO) {
        try {
            val formattedToken = token?.let { if (it.startsWith("Bearer ") || it.startsWith("token ")) it else "token $it" }
            gitHubApiService.getRepositoryDetails(owner, repo, formattedToken)
        } catch (e: Exception) {
            Log.e(tag, "Error getting repo details", e)
            throw e
        }
    }

    suspend fun getRepositoryReadme(owner: String, repo: String, token: String?): String = withContext(Dispatchers.IO) {
        try {
            val formattedToken = token?.let { if (it.startsWith("Bearer ") || it.startsWith("token ")) it else "token $it" }
            val response = gitHubApiService.getRepositoryReadme(owner, repo, formattedToken)
            if (response.isSuccessful) {
                response.body()?.string() ?: ""
            } else {
                Log.w(tag, "Readme not found: code ${response.code()}")
                ""
            }
        } catch (e: Exception) {
            Log.e(tag, "Error getting readme", e)
            ""
        }
    }

    suspend fun getRepositoryCommits(owner: String, repo: String, token: String?): List<GitHubCommitResponse> = withContext(Dispatchers.IO) {
        try {
            val formattedToken = token?.let { if (it.startsWith("Bearer ") || it.startsWith("token ")) it else "token $it" }
            gitHubApiService.getRepositoryCommits(owner, repo, perPage = 15, token = formattedToken)
        } catch (e: Exception) {
            Log.e(tag, "Error getting commits", e)
            emptyList()
        }
    }

    suspend fun getRepositoryIssues(owner: String, repo: String, token: String?): List<GitHubIssue> = withContext(Dispatchers.IO) {
        try {
            val formattedToken = token?.let { if (it.startsWith("Bearer ") || it.startsWith("token ")) it else "token $it" }
            gitHubApiService.getRepositoryIssues(owner, repo, state = "open", perPage = 15, token = formattedToken)
        } catch (e: Exception) {
            Log.e(tag, "Error getting issues", e)
            emptyList()
        }
    }

    suspend fun getUserProfile(username: String, token: String?): GitHubUser = withContext(Dispatchers.IO) {
        try {
            val formattedToken = token?.let { if (it.startsWith("Bearer ") || it.startsWith("token ")) it else "token $it" }
            gitHubApiService.getUserProfile(username, formattedToken)
        } catch (e: Exception) {
            Log.e(tag, "Error getting user profile", e)
            throw e
        }
    }

    suspend fun getUserRepositories(username: String, token: String?): List<GitHubRepo> = withContext(Dispatchers.IO) {
        try {
            val formattedToken = token?.let { if (it.startsWith("Bearer ") || it.startsWith("token ")) it else "token $it" }
            gitHubApiService.getUserRepositories(username, sort = "updated", perPage = 15, token = formattedToken)
        } catch (e: Exception) {
            Log.e(tag, "Error getting user repos", e)
            emptyList()
        }
    }

    // --- Gemini Summarization Logic ---

    suspend fun generateSummary(prompt: String, systemInstruction: String? = null): String = withContext(Dispatchers.IO) {
        val apiKey = BuildConfig.GEMINI_API_KEY
        if (apiKey == "MY_GEMINI_API_KEY" || apiKey.isBlank()) {
            return@withContext "Gemini API key is not configured. Please configure it in the AI Studio Secrets panel."
        }

        val request = GeminiRequest(
            contents = listOf(
                GeminiContent(parts = listOf(GeminiPart(text = prompt)))
            ),
            systemInstruction = systemInstruction?.let {
                GeminiContent(parts = listOf(GeminiPart(text = it)))
            }
        )

        try {
            val response = geminiApiService.generateContent(apiKey, request)
            response.candidates?.firstOrNull()?.content?.parts?.firstOrNull()?.text
                ?: "No summary could be generated by Gemini."
        } catch (e: Exception) {
            Log.e(tag, "Error calling Gemini API", e)
            "Error communicating with Gemini: ${e.localizedMessage ?: e.message}"
        }
    }
}
