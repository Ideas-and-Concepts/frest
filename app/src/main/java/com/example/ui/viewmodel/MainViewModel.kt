package com.example.ui.viewmodel

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import com.example.data.database.AppDatabase
import com.example.data.database.BookmarkedRepo
import com.example.data.database.SearchQuery
import com.example.data.api.RetrofitClients
import com.example.data.model.GitHubCommitResponse
import com.example.data.model.GitHubIssue
import com.example.data.model.GitHubRepo
import com.example.data.model.GitHubUser
import com.example.data.pref.PreferencesManager
import com.example.data.repository.GitHubRepository
import com.example.data.repository.LocalRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch

sealed interface SearchUiState {
    object Idle : SearchUiState
    object Loading : SearchUiState
    data class Success(val repos: List<GitHubRepo>, val users: List<GitHubUser>) : SearchUiState
    data class Error(val message: String) : SearchUiState
}

sealed interface ActiveRepoUiState {
    object Idle : ActiveRepoUiState
    object Loading : ActiveRepoUiState
    data class Success(
        val repo: GitHubRepo,
        val readme: String,
        val commits: List<GitHubCommitResponse>,
        val issues: List<GitHubIssue>
    ) : ActiveRepoUiState
    data class Error(val message: String) : ActiveRepoUiState
}

sealed interface GeminiUiState {
    object Idle : GeminiUiState
    object Loading : GeminiUiState
    data class Success(val response: String) : GeminiUiState
    data class Error(val message: String) : GeminiUiState
}

class MainViewModel(
    application: Application,
    private val localRepository: LocalRepository,
    private val gitHubRepository: GitHubRepository,
    private val prefs: PreferencesManager
) : AndroidViewModel(application) {

    // --- State Observables ---

    val bookmarkedRepos: StateFlow<List<BookmarkedRepo>> = localRepository.allBookmarks
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())

    val recentSearchQueries: StateFlow<List<SearchQuery>> = localRepository.recentQueries
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())

    private val _searchUiState = MutableStateFlow<SearchUiState>(SearchUiState.Idle)
    val searchUiState: StateFlow<SearchUiState> = _searchUiState.asStateFlow()

    private val _activeRepoUiState = MutableStateFlow<ActiveRepoUiState>(ActiveRepoUiState.Idle)
    val activeRepoUiState: StateFlow<ActiveRepoUiState> = _activeRepoUiState.asStateFlow()

    private val _geminiUiState = MutableStateFlow<GeminiUiState>(GeminiUiState.Idle)
    val geminiUiState: StateFlow<GeminiUiState> = _geminiUiState.asStateFlow()

    // Preferences/Settings State
    private val _gitHubToken = MutableStateFlow<String?>(prefs.getGitHubToken())
    val gitHubToken: StateFlow<String?> = _gitHubToken.asStateFlow()

    private val _selectedLanguage = MutableStateFlow(prefs.getFavoriteLanguage())
    val selectedLanguage: StateFlow<String> = _selectedLanguage.asStateFlow()

    // Active Repository Identifier currently selected for details or AI analysis
    private val _selectedRepo = MutableStateFlow<GitHubRepo?>(null)
    val selectedRepo: StateFlow<GitHubRepo?> = _selectedRepo.asStateFlow()

    fun saveGitHubToken(token: String?) {
        prefs.saveGitHubToken(token)
        _gitHubToken.value = token
    }

    fun saveFavoriteLanguage(lang: String) {
        prefs.saveFavoriteLanguage(lang)
        _selectedLanguage.value = lang
    }

    // --- Business Logic Operations ---

    fun searchGitHub(query: String) {
        if (query.isBlank()) return
        viewModelScope.launch {
            _searchUiState.value = SearchUiState.Loading
            localRepository.saveSearchQuery(query)
            try {
                // Determine if searching for user or repo
                val token = _gitHubToken.value
                val repos = if (query.startsWith("user:")) {
                    emptyList()
                } else {
                    gitHubRepository.searchRepositories(query, token)
                }

                val users = if (query.contains("/") || !query.startsWith("user:") && repos.isNotEmpty()) {
                    emptyList()
                } else {
                    val userQuery = query.removePrefix("user:").trim()
                    try {
                        listOf(gitHubRepository.getUserProfile(userQuery, token))
                    } catch (e: Exception) {
                        emptyList()
                    }
                }

                _searchUiState.value = SearchUiState.Success(repos, users)
            } catch (e: Exception) {
                _searchUiState.value = SearchUiState.Error(e.localizedMessage ?: "Failed to retrieve results")
            }
        }
    }

    fun selectRepository(owner: String, repoName: String) {
        viewModelScope.launch {
            _activeRepoUiState.value = ActiveRepoUiState.Loading
            _geminiUiState.value = GeminiUiState.Idle // Reset Gemini output
            try {
                val token = _gitHubToken.value
                val repoDetails = gitHubRepository.getRepositoryDetails(owner, repoName, token)
                _selectedRepo.value = repoDetails

                val readme = gitHubRepository.getRepositoryReadme(owner, repoName, token)
                val commits = gitHubRepository.getRepositoryCommits(owner, repoName, token)
                val issues = gitHubRepository.getRepositoryIssues(owner, repoName, token)

                _activeRepoUiState.value = ActiveRepoUiState.Success(
                    repo = repoDetails,
                    readme = readme,
                    commits = commits,
                    issues = issues
                )
            } catch (e: Exception) {
                _activeRepoUiState.value = ActiveRepoUiState.Error(e.localizedMessage ?: "Failed to load repository details")
            }
        }
    }

    fun selectRepositoryDirect(repo: GitHubRepo) {
        _selectedRepo.value = repo
        selectRepository(repo.owner.login, repo.name)
    }

    // --- Bookmark operations ---

    fun toggleBookmark(repo: GitHubRepo) {
        viewModelScope.launch {
            val isCurrentlyBookmarked = localRepository.isBookmarked(repo.id)
            if (isCurrentlyBookmarked) {
                localRepository.removeBookmark(repo.id)
            } else {
                localRepository.addBookmark(
                    BookmarkedRepo(
                        id = repo.id,
                        name = repo.name,
                        owner = repo.owner.login,
                        description = repo.description,
                        stars = repo.stargazersCount,
                        language = repo.language,
                        htmlUrl = repo.htmlUrl,
                        avatarUrl = repo.owner.avatarUrl
                    )
                )
            }
        }
    }

    fun toggleBookmark(repo: BookmarkedRepo) {
        viewModelScope.launch {
            localRepository.removeBookmark(repo.id)
        }
    }

    fun isBookmarkedFlow(repoId: Long): StateFlow<Boolean> {
        val flow = MutableStateFlow(false)
        viewModelScope.launch {
            flow.value = localRepository.isBookmarked(repoId)
        }
        return flow
    }

    // --- Gemini Prompts ---

    fun summarizeReadme(readmeText: String, repoName: String) {
        if (readmeText.isBlank()) {
            _geminiUiState.value = GeminiUiState.Success("This repository does not have a README file to summarize.")
            return
        }
        viewModelScope.launch {
            _geminiUiState.value = GeminiUiState.Loading
            val systemInstruction = "You are a senior software architect. Analyze the provided README for the repository '$repoName' and provide a concise, high-level structural overview. Bullet point the: 1. Core Purpose, 2. Key Features, 3. Technologies & Architecture, and 4. Quick-start Summary. Keep it clean, professional, and directly useful."
            val response = gitHubRepository.generateSummary(
                prompt = "Here is the repository README:\n\n$readmeText",
                systemInstruction = systemInstruction
            )
            _geminiUiState.value = GeminiUiState.Success(response)
        }
    }

    fun summarizeCommits(commits: List<GitHubCommitResponse>, repoName: String) {
        if (commits.isEmpty()) {
            _geminiUiState.value = GeminiUiState.Success("No recent commits available to summarize.")
            return
        }
        viewModelScope.launch {
            _geminiUiState.value = GeminiUiState.Loading
            val commitsText = commits.joinToString("\n") { commit ->
                "- [${commit.sha.take(7)}] by ${commit.commit.author.name}: ${commit.commit.message}"
            }
            val systemInstruction = "You are an expert tech lead. Analyze the list of recent commits for the repository '$repoName' and summarize the main focus of recent development. Highlight any major features, bug fixes, refactorings, or documentation updates. Format with neat markdown headers."
            val response = gitHubRepository.generateSummary(
                prompt = "Here are the recent commits:\n\n$commitsText",
                systemInstruction = systemInstruction
            )
            _geminiUiState.value = GeminiUiState.Success(response)
        }
    }

    fun draftReleaseNotes(commits: List<GitHubCommitResponse>, issues: List<GitHubIssue>, repoName: String) {
        viewModelScope.launch {
            _geminiUiState.value = GeminiUiState.Loading
            val commitsText = commits.take(15).joinToString("\n") { commit ->
                "- ${commit.commit.message} (${commit.sha.take(7)})"
            }
            val issuesText = issues.take(10).joinToString("\n") { issue ->
                "- Issue #${issue.number}: ${issue.title} [${issue.state}]"
            }
            val prompt = """
                Draft release notes for repository '$repoName'.
                
                Recent Commits:
                $commitsText
                
                Open Issues:
                $issuesText
            """.trimIndent()
            val systemInstruction = "You are a product release manager. Create a professional and exciting Draft Release Notes document based on the provided commits and open issues. Organize it into sections: '🚀 Features', '🐛 Bug Fixes', '⚙️ General Improvements', and '🛠️ Contributors'. Keep the tone encouraging, concise, and focused on user-facing benefits."
            val response = gitHubRepository.generateSummary(
                prompt = prompt,
                systemInstruction = systemInstruction
            )
            _geminiUiState.value = GeminiUiState.Success(response)
        }
    }

    fun deleteRecentQuery(query: String) {
        viewModelScope.launch {
            localRepository.deleteSearchQuery(query)
        }
    }

    fun clearSearchHistory() {
        viewModelScope.launch {
            localRepository.clearSearchHistory()
        }
    }
}

// --- ViewModel Factory ---

class MainViewModelFactory(
    private val application: Application
) : ViewModelProvider.Factory {
    @Suppress("UNCHECKED_CAST")
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        if (modelClass.isAssignableFrom(MainViewModel::class.java)) {
            val database = AppDatabase.getDatabase(application)
            val localRepository = LocalRepository(database.bookmarkedRepoDao(), database.searchHistoryDao())
            val gitHubRepository = GitHubRepository(RetrofitClients.gitHubService, RetrofitClients.geminiService)
            val prefs = PreferencesManager(application)
            return MainViewModel(application, localRepository, gitHubRepository, prefs) as T
        }
        throw IllegalArgumentException("Unknown ViewModel class")
    }
}
