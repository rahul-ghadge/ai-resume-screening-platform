package com.resumeai.dto.response;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.resumeai.model.*;
import lombok.*;

import java.time.Instant;
import java.util.List;
import java.util.Map;

// ═══════════════════════════════════════════════
//  GENERIC API WRAPPER
// ═══════════════════════════════════════════════

@Data @Builder @NoArgsConstructor @AllArgsConstructor
@JsonInclude(JsonInclude.Include.NON_NULL)
public class ApiResponse<T> {
    private boolean success;
    private String  message;
    private T       data;
    private int     statusCode;
    private Instant timestamp;
    private String  path;

    public static <T> ApiResponse<T> success(T data, String message) {
        return ApiResponse.<T>builder()
                .success(true).message(message).data(data)
                .statusCode(200).timestamp(Instant.now()).build();
    }

    public static <T> ApiResponse<T> created(T data, String message) {
        return ApiResponse.<T>builder()
                .success(true).message(message).data(data)
                .statusCode(201).timestamp(Instant.now()).build();
    }

    public static <T> ApiResponse<T> error(String message, int statusCode) {
        return ApiResponse.<T>builder()
                .success(false).message(message)
                .statusCode(statusCode).timestamp(Instant.now()).build();
    }
}

// ═══════════════════════════════════════════════
//  AUTH RESPONSE
// ═══════════════════════════════════════════════

@Data @Builder @NoArgsConstructor @AllArgsConstructor
@JsonInclude(JsonInclude.Include.NON_NULL)
class AuthResponse {
    private String accessToken;
    private String tokenType;
    private Long   expiresIn;
    private UserResponse user;
}

// ═══════════════════════════════════════════════
//  USER RESPONSE
// ═══════════════════════════════════════════════

@Data @Builder @NoArgsConstructor @AllArgsConstructor
@JsonInclude(JsonInclude.Include.NON_NULL)
class UserResponse {
    private String id;
    private String email;
    private String username;
    private String firstName;
    private String lastName;
    private String companyName;
    private java.util.Set<User.Role> roles;
    private Boolean isActive;
    private Instant createdAt;
}

// ═══════════════════════════════════════════════
//  RESUME RESPONSE
// ═══════════════════════════════════════════════

@Data @Builder @NoArgsConstructor @AllArgsConstructor
@JsonInclude(JsonInclude.Include.NON_NULL)
class ResumeResponse {
    private String  id;
    private String  candidateId;
    private String  candidateName;
    private String  candidateEmail;
    private String  phone;
    private String  location;
    private String  originalFilename;
    private Long    fileSizeBytes;
    private String  summary;
    private Double  totalExperienceYears;
    private List<String> technicalSkills;
    private List<String> softSkills;
    private List<String> certifications;
    private List<Resume.Education>      education;
    private List<Resume.WorkExperience> workExperience;
    private Resume.ProcessingStatus     processingStatus;
    private Double  aiConfidenceScore;
    private Boolean isActive;
    private Instant createdAt;
    private Instant updatedAt;
}

// ═══════════════════════════════════════════════
//  JOB RESPONSE
// ═══════════════════════════════════════════════

@Data @Builder @NoArgsConstructor @AllArgsConstructor
@JsonInclude(JsonInclude.Include.NON_NULL)
class JobPostingResponse {
    private String id;
    private String title;
    private String description;
    private String companyName;
    private String location;
    private Boolean remoteAllowed;
    private JobPosting.EmploymentType employmentType;
    private JobPosting.ExperienceLevel experienceLevel;
    private Integer minExperienceYears;
    private Integer maxExperienceYears;
    private Long salaryMin;
    private Long salaryMax;
    private String salaryCurrency;
    private List<String> requiredSkills;
    private List<String> preferredSkills;
    private JobPosting.JobStatus status;
    private Integer applicationCount;
    private Instant expiresAt;
    private Instant createdAt;
    private Instant updatedAt;
}

// ═══════════════════════════════════════════════
//  MATCH RESPONSE
// ═══════════════════════════════════════════════

@Data @Builder @NoArgsConstructor @AllArgsConstructor
@JsonInclude(JsonInclude.Include.NON_NULL)
class MatchResultResponse {
    private String id;
    private String resumeId;
    private String jobId;
    private String candidateId;
    private Double overallScore;
    private Double skillMatchScore;
    private Double experienceMatchScore;
    private Double educationMatchScore;
    private Double keywordMatchScore;
    private List<String> matchedSkills;
    private List<String> missingSkills;
    private List<String> bonusSkills;
    private Map<String, Double> scoreBreakdown;
    private String aiSummary;
    private MatchResult.MatchRecommendation recommendation;
    private MatchResult.MatchStatus status;
    private String recruiterNotes;
    private Instant createdAt;
    private Instant updatedAt;
}

// ═══════════════════════════════════════════════
//  DASHBOARD / STATS RESPONSE
// ═══════════════════════════════════════════════

@Data @Builder @NoArgsConstructor @AllArgsConstructor
@JsonInclude(JsonInclude.Include.NON_NULL)
class RecruiterDashboardResponse {
    private Long   totalJobPostings;
    private Long   activeJobPostings;
    private Long   totalApplications;
    private Long   shortlistedCandidates;
    private Long   hiredCandidates;
    private Double avgMatchScore;
    private List<JobSummary> recentJobs;
    private List<TopCandidate> topCandidates;
}

@Data @Builder @NoArgsConstructor @AllArgsConstructor
class JobSummary {
    private String id;
    private String title;
    private Long   applicationCount;
    private JobPosting.JobStatus status;
    private Instant createdAt;
}

@Data @Builder @NoArgsConstructor @AllArgsConstructor
class TopCandidate {
    private String resumeId;
    private String candidateName;
    private String candidateEmail;
    private String jobTitle;
    private Double matchScore;
    private MatchResult.MatchRecommendation recommendation;
}

// ═══════════════════════════════════════════════
//  PAGINATION RESPONSE
// ═══════════════════════════════════════════════

@Data @Builder @NoArgsConstructor @AllArgsConstructor
class PagedResponse<T> {
    private List<T> content;
    private int     pageNumber;
    private int     pageSize;
    private long    totalElements;
    private int     totalPages;
    private boolean first;
    private boolean last;
}

// ═══════════════════════════════════════════════
//  UPLOAD RESPONSE
// ═══════════════════════════════════════════════

@Data @Builder @NoArgsConstructor @AllArgsConstructor
class ResumeUploadResponse {
    private String resumeId;
    private String originalFilename;
    private Long   fileSizeBytes;
    private Resume.ProcessingStatus processingStatus;
    private String message;
    private Instant submittedAt;
}
