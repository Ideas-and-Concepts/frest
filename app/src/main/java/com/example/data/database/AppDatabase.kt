package com.example.data.database

import android.content.Context
import androidx.room.Dao
import androidx.room.Database
import androidx.room.Entity
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.PrimaryKey
import androidx.room.Query
import androidx.room.Room
import androidx.room.RoomDatabase
import kotlinx.coroutines.flow.Flow

// --- Entities ---

@Entity(tableName = "bookmarked_repositories")
data class BookmarkedRepo(
    @PrimaryKey val id: Long,
    val name: String,
    val owner: String,
    val description: String?,
    val stars: Int,
    val language: String?,
    val htmlUrl: String,
    val avatarUrl: String?,
    val timestamp: Long = System.currentTimeMillis()
)

@Entity(tableName = "search_history")
data class SearchQuery(
    @PrimaryKey val query: String,
    val timestamp: Long = System.currentTimeMillis()
)

// --- DAOs ---

@Dao
interface BookmarkedRepoDao {
    @Query("SELECT * FROM bookmarked_repositories ORDER BY timestamp DESC")
    fun getAllBookmarks(): Flow<List<BookmarkedRepo>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertBookmark(repo: BookmarkedRepo)

    @Query("DELETE FROM bookmarked_repositories WHERE id = :id")
    suspend fun deleteBookmarkById(id: Long)

    @Query("SELECT EXISTS(SELECT 1 FROM bookmarked_repositories WHERE id = :id LIMIT 1)")
    suspend fun isBookmarked(id: Long): Boolean
}

@Dao
interface SearchHistoryDao {
    @Query("SELECT * FROM search_history ORDER BY timestamp DESC LIMIT 10")
    fun getRecentQueries(): Flow<List<SearchQuery>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertQuery(query: SearchQuery)

    @Query("DELETE FROM search_history WHERE `query` = :query")
    suspend fun deleteQuery(query: String)

    @Query("DELETE FROM search_history")
    suspend fun clearHistory()
}

// --- Database ---

@Database(entities = [BookmarkedRepo::class, SearchQuery::class], version = 1, exportSchema = false)
abstract class AppDatabase : RoomDatabase() {
    abstract fun bookmarkedRepoDao(): BookmarkedRepoDao
    abstract fun searchHistoryDao(): SearchHistoryDao

    companion object {
        @Volatile
        private var INSTANCE: AppDatabase? = null

        fun getDatabase(context: Context): AppDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    "github_streamline_database"
                ).fallbackToDestructiveMigration().build()
                INSTANCE = instance
                instance
            }
        }
    }
}
