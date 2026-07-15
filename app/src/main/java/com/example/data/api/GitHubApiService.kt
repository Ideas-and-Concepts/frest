package com.example.data.api

import com.example.data.model.GitHubCommitResponse
import com.example.data.model.GitHubIssue
import com.example.data.model.GitHubRepo
import com.example.data.model.GitHubUser
import com.example.data.model.RepoSearchResponse
import okhttp3.ResponseBody
import retrofit2.Response
import retrofit2.http.GET
import retrofit2.http.Header
import retrofit2.http.Headers
import retrofit2.http.Path
import retrofit2.http.Query

interface GitHubApiService {

    @GET("search/repositories")
    suspend fun searchRepositories(
        @Query("q") query: String,
        @Query("sort") sort: String? = null,
        @Query("order") order: String? = null,
        @Header("Authorization") token: String? = null
    ): RepoSearchResponse

    @GET("repos/{owner}/{repo}")
    suspend fun getRepositoryDetails(
        @Path("owner") owner: String,
        @Path("repo") repo: String,
        @Header("Authorization") token: String? = null
    ): GitHubRepo

    @GET("repos/{owner}/{repo}/readme")
    @Headers("Accept: application/vnd.github.raw")
    suspend fun getRepositoryReadme(
        @Path("owner") owner: String,
        @Path("repo") repo: String,
        @Header("Authorization") token: String? = null
    ): Response<ResponseBody>

    @GET("repos/{owner}/{repo}/commits")
    suspend fun getRepositoryCommits(
        @Path("owner") owner: String,
        @Path("repo") repo: String,
        @Query("per_page") perPage: Int = 15,
        @Header("Authorization") token: String? = null
    ): List<GitHubCommitResponse>

    @GET("repos/{owner}/{repo}/issues")
    suspend fun getRepositoryIssues(
        @Path("owner") owner: String,
        @Path("repo") repo: String,
        @Query("state") state: String = "open",
        @Query("per_page") perPage: Int = 15,
        @Header("Authorization") token: String? = null
    ): List<GitHubIssue>

    @GET("users/{username}")
    suspend fun getUserProfile(
        @Path("username") username: String,
        @Header("Authorization") token: String? = null
    ): GitHubUser

    @GET("users/{username}/repos")
    suspend fun getUserRepositories(
        @Path("username") username: String,
        @Query("sort") sort: String = "updated",
        @Query("per_page") perPage: Int = 15,
        @Header("Authorization") token: String? = null
    ): List<GitHubRepo>
}
