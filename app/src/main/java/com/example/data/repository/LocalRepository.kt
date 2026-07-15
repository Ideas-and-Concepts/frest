package com.example.data.repository

import com.example.data.database.BookmarkedRepo
import com.example.data.database.BookmarkedRepoDao
import com.example.data.database.SearchQuery
import com.example.data.database.SearchHistoryDao
import kotlinx.coroutines.flow.Flow

class LocalRepository(
    private val bookmarkedRepoDao: BookmarkedRepoDao,
    private val searchHistoryDao: SearchHistoryDao
) {
    val allBookmarks: Flow<List<BookmarkedRepo>> = bookmarkedRepoDao.getAllBookmarks()
    val recentQueries: Flow<List<SearchQuery>> = searchHistoryDao.getRecentQueries()

    suspend fun addBookmark(repo: BookmarkedRepo) {
        bookmarkedRepoDao.insertBookmark(repo)
    }

    suspend fun removeBookmark(id: Long) {
        bookmarkedRepoDao.deleteBookmarkById(id)
    }

    suspend fun isBookmarked(id: Long): Boolean {
        return bookmarkedRepoDao.isBookmarked(id)
    }

    suspend fun saveSearchQuery(queryText: String) {
        if (queryText.isNotBlank()) {
            searchHistoryDao.insertQuery(SearchQuery(queryText.trim()))
        }
    }

    suspend fun deleteSearchQuery(queryText: String) {
        searchHistoryDao.deleteQuery(queryText)
    }

    suspend fun clearSearchHistory() {
        searchHistoryDao.clearHistory()
    }
}
