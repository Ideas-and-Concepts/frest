package com.example.data.model

import com.squareup.moshi.Json
import com.squareup.moshi.JsonClass

@JsonClass(generateAdapter = true)
data class RepoSearchResponse(
    @Json(name = "total_count") val totalCount: Int,
    @Json(name = "incomplete_results") val incompleteResults: Boolean,
    @Json(name = "items") val items: List<GitHubRepo>
)

@JsonClass(generateAdapter = true)
data class GitHubRepo(
    @Json(name = "id") val id: Long,
    @Json(name = "name") val name: String,
    @Json(name = "full_name") val fullName: String,
    @Json(name = "owner") val owner: GitHubUser,
    @Json(name = "description") val description: String?,
    @Json(name = "stargazers_count") val stargazersCount: Int,
    @Json(name = "watchers_count") val watchersCount: Int,
    @Json(name = "forks_count") val forksCount: Int,
    @Json(name = "language") val language: String?,
    @Json(name = "html_url") val htmlUrl: String,
    @Json(name = "updated_at") val updatedAt: String,
    @Json(name = "open_issues_count") val openIssuesCount: Int? = 0
)

@JsonClass(generateAdapter = true)
data class GitHubUser(
    @Json(name = "id") val id: Long,
    @Json(name = "login") val login: String,
    @Json(name = "avatar_url") val avatarUrl: String,
    @Json(name = "html_url") val htmlUrl: String,
    @Json(name = "name") val name: String? = null,
    @Json(name = "company") val company: String? = null,
    @Json(name = "blog") val blog: String? = null,
    @Json(name = "location") val location: String? = null,
    @Json(name = "bio") val bio: String? = null,
    @Json(name = "public_repos") val publicRepos: Int? = 0,
    @Json(name = "followers") val followers: Int? = 0,
    @Json(name = "following") val following: Int? = 0
)

@JsonClass(generateAdapter = true)
data class GitHubCommitResponse(
    @Json(name = "sha") val sha: String,
    @Json(name = "commit") val commit: CommitDetails,
    @Json(name = "author") val author: GitHubUser? = null
)

@JsonClass(generateAdapter = true)
data class CommitDetails(
    @Json(name = "message") val message: String,
    @Json(name = "author") val author: CommitAuthor
)

@JsonClass(generateAdapter = true)
data class CommitAuthor(
    @Json(name = "name") val name: String,
    @Json(name = "email") val email: String,
    @Json(name = "date") val date: String
)

@JsonClass(generateAdapter = true)
data class GitHubIssue(
    @Json(name = "id") val id: Long,
    @Json(name = "number") val number: Int,
    @Json(name = "title") val title: String,
    @Json(name = "body") val body: String?,
    @Json(name = "state") val state: String,
    @Json(name = "user") val user: GitHubUser,
    @Json(name = "created_at") val createdAt: String,
    @Json(name = "comments") val comments: Int? = 0
)
