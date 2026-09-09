package com.legacybank.domain;
import java.time.LocalDateTime;

public abstract class BaseEntity {
    protected String id;
    protected LocalDateTime createdAt;

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
}