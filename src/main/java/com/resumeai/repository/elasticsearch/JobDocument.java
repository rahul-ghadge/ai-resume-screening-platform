package com.resumeai.repository.elasticsearch;

import lombok.*;
import org.springframework.data.annotation.Id;
import org.springframework.data.elasticsearch.annotations.*;
import org.springframework.data.elasticsearch.repository.ElasticsearchRepository;
import org.springframework.stereotype.Repository;

import java.time.Instant;
import java.util.List;

@Document(indexName = "jobs")
@Data @NoArgsConstructor @AllArgsConstructor @Builder
public class JobDocument {

    @Id
    private String id;

    @Field(type = FieldType.Text, analyzer = "english")
    private String title;

    @Field(type = FieldType.Text, analyzer = "english")
    private String description;

    @Field(type = FieldType.Keyword)
    private String companyName;

    @Field(type = FieldType.Keyword)
    private List<String> requiredSkills;

    @Field(type = FieldType.Keyword)
    private List<String> preferredSkills;

    @Field(type = FieldType.Keyword)
    private String status;

    @Field(type = FieldType.Text)
    private String location;

    @Field(type = FieldType.Integer)
    private Integer minExperienceYears;

    @Field(type = FieldType.Date)
    private Instant createdAt;
}

@Repository
interface JobSearchRepository extends ElasticsearchRepository<JobDocument, String> {

    List<JobDocument> findByRequiredSkillsIn(List<String> skills);

    List<JobDocument> findByStatusAndMinExperienceYearsLessThanEqual(
            String status, Integer experienceYears);
}
