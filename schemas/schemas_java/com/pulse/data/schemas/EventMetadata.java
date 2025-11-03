
package com.pulse.data.schemas;

import java.io.Serializable;
import java.util.Date;
import javax.annotation.processing.Generated;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyDescription;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;


/**
 * EventMetadata
 * <p>
 * Base metadata for all events in the Pulse platform
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder({
    "datumIntId",
    "datumStringId",
    "datumKey",
    "datumTimestamp",
    "datumDatetime",
    "datumPublishedTime",
    "datumReceivedTime",
    "eventVersion",
    "eventPayload"
})
@Generated("jsonschema2pojo")
public class EventMetadata implements Serializable
{

    /**
     * Unique integer identifier for this datum type
     * (Required)
     * 
     */
    @JsonProperty("datumIntId")
    @JsonPropertyDescription("Unique integer identifier for this datum type")
    private Long datumIntId;
    /**
     * Human-readable string identifier for this datum type
     * (Required)
     * 
     */
    @JsonProperty("datumStringId")
    @JsonPropertyDescription("Human-readable string identifier for this datum type")
    private String datumStringId;
    /**
     * Unique key identifying this specific datum instance
     * (Required)
     * 
     */
    @JsonProperty("datumKey")
    @JsonPropertyDescription("Unique key identifying this specific datum instance")
    private String datumKey;
    /**
     * Epoch time (milliseconds) representing the datum time
     * (Required)
     * 
     */
    @JsonProperty("datumTimestamp")
    @JsonPropertyDescription("Epoch time (milliseconds) representing the datum time")
    private Long datumTimestamp;
    /**
     * Optional ISO-8601 datetime corresponding to datumTimestamp for readability
     * 
     */
    @JsonProperty("datumDatetime")
    @JsonPropertyDescription("Optional ISO-8601 datetime corresponding to datumTimestamp for readability")
    private Date datumDatetime;
    /**
     * Epoch time (milliseconds) at which the datum was published
     * 
     */
    @JsonProperty("datumPublishedTime")
    @JsonPropertyDescription("Epoch time (milliseconds) at which the datum was published")
    private Long datumPublishedTime;
    /**
     * Epoch time (milliseconds) at which the datum was received
     * 
     */
    @JsonProperty("datumReceivedTime")
    @JsonPropertyDescription("Epoch time (milliseconds) at which the datum was received")
    private Long datumReceivedTime;
    /**
     * Version of this event schema for compatibility tracking
     * 
     */
    @JsonProperty("eventVersion")
    @JsonPropertyDescription("Version of this event schema for compatibility tracking")
    private Long eventVersion;
    /**
     * The event payload (structure defined by the event type)
     * (Required)
     * 
     */
    @JsonProperty("eventPayload")
    @JsonPropertyDescription("The event payload (structure defined by the event type)")
    private EventPayload eventPayload;
    private final static long serialVersionUID = 6547140007466371730L;

    /**
     * No args constructor for use in serialization
     * 
     */
    public EventMetadata() {
    }

    /**
     * 
     * @param datumStringId
     *     Human-readable string identifier for this datum type.
     * @param datumIntId
     *     Unique integer identifier for this datum type.
     * @param datumReceivedTime
     *     Epoch time (milliseconds) at which the datum was received.
     * @param eventVersion
     *     Version of this event schema for compatibility tracking.
     * @param datumKey
     *     Unique key identifying this specific datum instance.
     * @param datumTimestamp
     *     Epoch time (milliseconds) representing the datum time.
     * @param datumPublishedTime
     *     Epoch time (milliseconds) at which the datum was published.
     * @param eventPayload
     *     The event payload (structure defined by the event type).
     * @param datumDatetime
     *     Optional ISO-8601 datetime corresponding to datumTimestamp for readability.
     */
    public EventMetadata(Long datumIntId, String datumStringId, String datumKey, Long datumTimestamp, Date datumDatetime, Long datumPublishedTime, Long datumReceivedTime, Long eventVersion, EventPayload eventPayload) {
        super();
        this.datumIntId = datumIntId;
        this.datumStringId = datumStringId;
        this.datumKey = datumKey;
        this.datumTimestamp = datumTimestamp;
        this.datumDatetime = datumDatetime;
        this.datumPublishedTime = datumPublishedTime;
        this.datumReceivedTime = datumReceivedTime;
        this.eventVersion = eventVersion;
        this.eventPayload = eventPayload;
    }

    /**
     * Unique integer identifier for this datum type
     * (Required)
     * 
     */
    @JsonProperty("datumIntId")
    public Long getDatumIntId() {
        return datumIntId;
    }

    /**
     * Unique integer identifier for this datum type
     * (Required)
     * 
     */
    @JsonProperty("datumIntId")
    public void setDatumIntId(Long datumIntId) {
        this.datumIntId = datumIntId;
    }

    public EventMetadata withDatumIntId(Long datumIntId) {
        this.datumIntId = datumIntId;
        return this;
    }

    /**
     * Human-readable string identifier for this datum type
     * (Required)
     * 
     */
    @JsonProperty("datumStringId")
    public String getDatumStringId() {
        return datumStringId;
    }

    /**
     * Human-readable string identifier for this datum type
     * (Required)
     * 
     */
    @JsonProperty("datumStringId")
    public void setDatumStringId(String datumStringId) {
        this.datumStringId = datumStringId;
    }

    public EventMetadata withDatumStringId(String datumStringId) {
        this.datumStringId = datumStringId;
        return this;
    }

    /**
     * Unique key identifying this specific datum instance
     * (Required)
     * 
     */
    @JsonProperty("datumKey")
    public String getDatumKey() {
        return datumKey;
    }

    /**
     * Unique key identifying this specific datum instance
     * (Required)
     * 
     */
    @JsonProperty("datumKey")
    public void setDatumKey(String datumKey) {
        this.datumKey = datumKey;
    }

    public EventMetadata withDatumKey(String datumKey) {
        this.datumKey = datumKey;
        return this;
    }

    /**
     * Epoch time (milliseconds) representing the datum time
     * (Required)
     * 
     */
    @JsonProperty("datumTimestamp")
    public Long getDatumTimestamp() {
        return datumTimestamp;
    }

    /**
     * Epoch time (milliseconds) representing the datum time
     * (Required)
     * 
     */
    @JsonProperty("datumTimestamp")
    public void setDatumTimestamp(Long datumTimestamp) {
        this.datumTimestamp = datumTimestamp;
    }

    public EventMetadata withDatumTimestamp(Long datumTimestamp) {
        this.datumTimestamp = datumTimestamp;
        return this;
    }

    /**
     * Optional ISO-8601 datetime corresponding to datumTimestamp for readability
     * 
     */
    @JsonProperty("datumDatetime")
    public Date getDatumDatetime() {
        return datumDatetime;
    }

    /**
     * Optional ISO-8601 datetime corresponding to datumTimestamp for readability
     * 
     */
    @JsonProperty("datumDatetime")
    public void setDatumDatetime(Date datumDatetime) {
        this.datumDatetime = datumDatetime;
    }

    public EventMetadata withDatumDatetime(Date datumDatetime) {
        this.datumDatetime = datumDatetime;
        return this;
    }

    /**
     * Epoch time (milliseconds) at which the datum was published
     * 
     */
    @JsonProperty("datumPublishedTime")
    public Long getDatumPublishedTime() {
        return datumPublishedTime;
    }

    /**
     * Epoch time (milliseconds) at which the datum was published
     * 
     */
    @JsonProperty("datumPublishedTime")
    public void setDatumPublishedTime(Long datumPublishedTime) {
        this.datumPublishedTime = datumPublishedTime;
    }

    public EventMetadata withDatumPublishedTime(Long datumPublishedTime) {
        this.datumPublishedTime = datumPublishedTime;
        return this;
    }

    /**
     * Epoch time (milliseconds) at which the datum was received
     * 
     */
    @JsonProperty("datumReceivedTime")
    public Long getDatumReceivedTime() {
        return datumReceivedTime;
    }

    /**
     * Epoch time (milliseconds) at which the datum was received
     * 
     */
    @JsonProperty("datumReceivedTime")
    public void setDatumReceivedTime(Long datumReceivedTime) {
        this.datumReceivedTime = datumReceivedTime;
    }

    public EventMetadata withDatumReceivedTime(Long datumReceivedTime) {
        this.datumReceivedTime = datumReceivedTime;
        return this;
    }

    /**
     * Version of this event schema for compatibility tracking
     * 
     */
    @JsonProperty("eventVersion")
    public Long getEventVersion() {
        return eventVersion;
    }

    /**
     * Version of this event schema for compatibility tracking
     * 
     */
    @JsonProperty("eventVersion")
    public void setEventVersion(Long eventVersion) {
        this.eventVersion = eventVersion;
    }

    public EventMetadata withEventVersion(Long eventVersion) {
        this.eventVersion = eventVersion;
        return this;
    }

    /**
     * The event payload (structure defined by the event type)
     * (Required)
     * 
     */
    @JsonProperty("eventPayload")
    public EventPayload getEventPayload() {
        return eventPayload;
    }

    /**
     * The event payload (structure defined by the event type)
     * (Required)
     * 
     */
    @JsonProperty("eventPayload")
    public void setEventPayload(EventPayload eventPayload) {
        this.eventPayload = eventPayload;
    }

    public EventMetadata withEventPayload(EventPayload eventPayload) {
        this.eventPayload = eventPayload;
        return this;
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append(EventMetadata.class.getName()).append('@').append(Integer.toHexString(System.identityHashCode(this))).append('[');
        sb.append("datumIntId");
        sb.append('=');
        sb.append(((this.datumIntId == null)?"<null>":this.datumIntId));
        sb.append(',');
        sb.append("datumStringId");
        sb.append('=');
        sb.append(((this.datumStringId == null)?"<null>":this.datumStringId));
        sb.append(',');
        sb.append("datumKey");
        sb.append('=');
        sb.append(((this.datumKey == null)?"<null>":this.datumKey));
        sb.append(',');
        sb.append("datumTimestamp");
        sb.append('=');
        sb.append(((this.datumTimestamp == null)?"<null>":this.datumTimestamp));
        sb.append(',');
        sb.append("datumDatetime");
        sb.append('=');
        sb.append(((this.datumDatetime == null)?"<null>":this.datumDatetime));
        sb.append(',');
        sb.append("datumPublishedTime");
        sb.append('=');
        sb.append(((this.datumPublishedTime == null)?"<null>":this.datumPublishedTime));
        sb.append(',');
        sb.append("datumReceivedTime");
        sb.append('=');
        sb.append(((this.datumReceivedTime == null)?"<null>":this.datumReceivedTime));
        sb.append(',');
        sb.append("eventVersion");
        sb.append('=');
        sb.append(((this.eventVersion == null)?"<null>":this.eventVersion));
        sb.append(',');
        sb.append("eventPayload");
        sb.append('=');
        sb.append(((this.eventPayload == null)?"<null>":this.eventPayload));
        sb.append(',');
        if (sb.charAt((sb.length()- 1)) == ',') {
            sb.setCharAt((sb.length()- 1), ']');
        } else {
            sb.append(']');
        }
        return sb.toString();
    }

    @Override
    public int hashCode() {
        int result = 1;
        result = ((result* 31)+((this.datumStringId == null)? 0 :this.datumStringId.hashCode()));
        result = ((result* 31)+((this.datumIntId == null)? 0 :this.datumIntId.hashCode()));
        result = ((result* 31)+((this.datumReceivedTime == null)? 0 :this.datumReceivedTime.hashCode()));
        result = ((result* 31)+((this.eventVersion == null)? 0 :this.eventVersion.hashCode()));
        result = ((result* 31)+((this.datumKey == null)? 0 :this.datumKey.hashCode()));
        result = ((result* 31)+((this.datumTimestamp == null)? 0 :this.datumTimestamp.hashCode()));
        result = ((result* 31)+((this.datumPublishedTime == null)? 0 :this.datumPublishedTime.hashCode()));
        result = ((result* 31)+((this.eventPayload == null)? 0 :this.eventPayload.hashCode()));
        result = ((result* 31)+((this.datumDatetime == null)? 0 :this.datumDatetime.hashCode()));
        return result;
    }

    @Override
    public boolean equals(Object other) {
        if (other == this) {
            return true;
        }
        if ((other instanceof EventMetadata) == false) {
            return false;
        }
        EventMetadata rhs = ((EventMetadata) other);
        return ((((((((((this.datumStringId == rhs.datumStringId)||((this.datumStringId!= null)&&this.datumStringId.equals(rhs.datumStringId)))&&((this.datumIntId == rhs.datumIntId)||((this.datumIntId!= null)&&this.datumIntId.equals(rhs.datumIntId))))&&((this.datumReceivedTime == rhs.datumReceivedTime)||((this.datumReceivedTime!= null)&&this.datumReceivedTime.equals(rhs.datumReceivedTime))))&&((this.eventVersion == rhs.eventVersion)||((this.eventVersion!= null)&&this.eventVersion.equals(rhs.eventVersion))))&&((this.datumKey == rhs.datumKey)||((this.datumKey!= null)&&this.datumKey.equals(rhs.datumKey))))&&((this.datumTimestamp == rhs.datumTimestamp)||((this.datumTimestamp!= null)&&this.datumTimestamp.equals(rhs.datumTimestamp))))&&((this.datumPublishedTime == rhs.datumPublishedTime)||((this.datumPublishedTime!= null)&&this.datumPublishedTime.equals(rhs.datumPublishedTime))))&&((this.eventPayload == rhs.eventPayload)||((this.eventPayload!= null)&&this.eventPayload.equals(rhs.eventPayload))))&&((this.datumDatetime == rhs.datumDatetime)||((this.datumDatetime!= null)&&this.datumDatetime.equals(rhs.datumDatetime))));
    }

}
