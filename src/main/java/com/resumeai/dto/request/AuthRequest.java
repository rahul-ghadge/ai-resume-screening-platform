package com.resumeai.dto.request;

import com.resumeai.model.JobPosting;
import jakarta.validation.constraints.*;
import lombok.Data;

import java.time.Instant;
import java.util.List;

// ═══════════════════════════════════════════════
//  AUTH REQUESTS
// ═══════════════════════════════════════════════

public class AuthRequest {

    @Data
    public static class Register {
        @NotBlank @Email
        private String email;

        @NotBlank @Size(min = 3, max = 50)
        private String username;

        @NotBlank @Size(min = 8, max = 100)
        private String password;

        @NotBlank
        private String firstName;

        @NotBlank
        private String lastName;

        private String phone;
        private String companyName;

        @NotNull
        private com.resumeai.model.User.Role role;
    }

    @Data
    public static class Login {
        @NotBlank
        private String usernameOrEmail;

        @NotBlank
        private String password;
    }
}

// ═══════════════════════════════════════════════
//  JOB POSTING REQUESTS
// ═══════════════════════════════════════════════

class JobPostingRequest {

    @Data
    public static class Create {
        @NotBlank @Size(max = 200)
        private String title;

        @NotBlank
        private String description;

        @NotBlank
        private String companyName;

        private String location;
        private Boolean remoteAllowed;

        @NotNull
        private JobPosting.EmploymentType employmentType;

        @NotNull
        private JobPosting.ExperienceLevel experienceLevel;

        @Min(0) @Max(40)
        private Integer minExperienceYears;

        @Min(0) @Max(40)
        private Integer maxExperienceYears;

        private Long salaryMin;
        private Long salaryMax;
        private String salaryCurrency;

        @NotEmpty
        private List<String> requiredSkills;

        private List<String> preferredSkills;
        private List<String> responsibilities;
        private List<String> benefits;
        private List<String> tags;
        private String requiredEducation;
        private Instant expiresAt;
    }

    @Data
    public static class Update extends Create {
        private JobPosting.JobStatus status;
    }
}

// ═══════════════════════════════════════════════
//  MATCH REQUEST
// ═══════════════════════════════════════════════

class MatchRequest {

    @Data
    public static class TriggerMatch {
        @NotBlank
        private String resumeId;

        @NotBlank
        private String jobId;
    }

    @Data
    public static class BulkMatch {
        @NotBlank
        private String jobId;

        @Min(0) @Max(100)
        private double scoreThreshold = 60.0;
    }

    @Data
    public static class UpdateStatus {
        @NotNull
        private com.resumeai.model.MatchResult.MatchStatus status;

        private String recruiterNotes;
    }
}

// ═══════════════════════════════════════════════
//  SEARCH REQUEST
// ═══════════════════════════════════════════════

class SearchRequest {

    @Data
    public static class ResumeSearch {
        private String keyword;
        private List<String> skills;
        private Double minExperience;
        private Double maxExperience;
        private String location;
        private String processingStatus;
        private int page  = 0;
        private int size  = 20;
        private String sortBy  = "createdAt";
        private String sortDir = "desc";
    }

    @Data
    public static class JobSearch {
        private String keyword;
        private List<String> skills;
        private String location;
        private Boolean remoteAllowed;
        private JobPosting.EmploymentType employmentType;
        private JobPosting.ExperienceLevel experienceLevel;
        private Long salaryMin;
        private Long salaryMax;
        private int page  = 0;
        private int size  = 20;
    }
}
