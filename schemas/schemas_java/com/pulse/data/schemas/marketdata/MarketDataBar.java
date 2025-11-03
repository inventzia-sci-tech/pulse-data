
package com.pulse.data.schemas.marketdata;

import java.io.Serializable;
import java.math.BigDecimal;
import java.util.Date;
import javax.annotation.processing.Generated;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyDescription;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;


/**
 * MarketDataBar
 * <p>
 * Schema for a cdf (common data format) market data bar
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder({
    "symb",
    "op",
    "hi",
    "lo",
    "cl",
    "vlm",
    "vwap",
    "datetime",
    "count",
    "timestamp",
    "date",
    "expiry",
    "strike",
    "symExp"
})
@Generated("jsonschema2pojo")
public class MarketDataBar implements Serializable
{

    /**
     * Instrument symbol or identifier
     * (Required)
     * 
     */
    @JsonProperty("symb")
    @JsonPropertyDescription("Instrument symbol or identifier")
    private String symb;
    /**
     * Open price
     * (Required)
     * 
     */
    @JsonProperty("op")
    @JsonPropertyDescription("Open price")
    private BigDecimal op;
    /**
     * High price
     * (Required)
     * 
     */
    @JsonProperty("hi")
    @JsonPropertyDescription("High price")
    private BigDecimal hi;
    /**
     * Low price
     * (Required)
     * 
     */
    @JsonProperty("lo")
    @JsonPropertyDescription("Low price")
    private BigDecimal lo;
    /**
     * Close price
     * (Required)
     * 
     */
    @JsonProperty("cl")
    @JsonPropertyDescription("Close price")
    private BigDecimal cl;
    /**
     * Volume traded during this bar
     * (Required)
     * 
     */
    @JsonProperty("vlm")
    @JsonPropertyDescription("Volume traded during this bar")
    private BigDecimal vlm;
    /**
     * Volume-weighted average price (optional)
     * 
     */
    @JsonProperty("vwap")
    @JsonPropertyDescription("Volume-weighted average price (optional)")
    private BigDecimal vwap;
    /**
     * ISO 8601 timestamp representing the bar’s open/close time
     * (Required)
     * 
     */
    @JsonProperty("datetime")
    @JsonPropertyDescription("ISO 8601 timestamp representing the bar\u2019s open/close time")
    private Date datetime;
    /**
     * Number of trades aggregated in this bar (optional)
     * 
     */
    @JsonProperty("count")
    @JsonPropertyDescription("Number of trades aggregated in this bar (optional)")
    private Long count;
    /**
     * Epoch timestamp (milliseconds) when the bar was generated or received
     * (Required)
     * 
     */
    @JsonProperty("timestamp")
    @JsonPropertyDescription("Epoch timestamp (milliseconds) when the bar was generated or received")
    private Long timestamp;
    /**
     * Trading date for the bar
     * (Required)
     * 
     */
    @JsonProperty("date")
    @JsonPropertyDescription("Trading date for the bar")
    private String date;
    /**
     * Option or futures expiry (optional)
     * 
     */
    @JsonProperty("expiry")
    @JsonPropertyDescription("Option or futures expiry (optional)")
    private String expiry;
    /**
     * Option strike price (optional)
     * 
     */
    @JsonProperty("strike")
    @JsonPropertyDescription("Option strike price (optional)")
    private BigDecimal strike;
    /**
     * Symbol + expiry composite identifier (optional)
     * 
     */
    @JsonProperty("symExp")
    @JsonPropertyDescription("Symbol + expiry composite identifier (optional)")
    private String symExp;
    private final static long serialVersionUID = 1383539447548073742L;

    /**
     * No args constructor for use in serialization
     * 
     */
    public MarketDataBar() {
    }

    /**
     * 
     * @param date
     *     Trading date for the bar.
     * @param op
     *     Open price.
     * @param hi
     *     High price.
     * @param lo
     *     Low price.
     * @param vwap
     *     Volume-weighted average price (optional).
     * @param strike
     *     Option strike price (optional).
     * @param count
     *     Number of trades aggregated in this bar (optional).
     * @param cl
     *     Close price.
     * @param symb
     *     Instrument symbol or identifier.
     * @param symExp
     *     Symbol + expiry composite identifier (optional).
     * @param datetime
     *     ISO 8601 timestamp representing the bar’s open/close time.
     * @param vlm
     *     Volume traded during this bar.
     * @param expiry
     *     Option or futures expiry (optional).
     * @param timestamp
     *     Epoch timestamp (milliseconds) when the bar was generated or received.
     */
    public MarketDataBar(String symb, BigDecimal op, BigDecimal hi, BigDecimal lo, BigDecimal cl, BigDecimal vlm, BigDecimal vwap, Date datetime, Long count, Long timestamp, String date, String expiry, BigDecimal strike, String symExp) {
        super();
        this.symb = symb;
        this.op = op;
        this.hi = hi;
        this.lo = lo;
        this.cl = cl;
        this.vlm = vlm;
        this.vwap = vwap;
        this.datetime = datetime;
        this.count = count;
        this.timestamp = timestamp;
        this.date = date;
        this.expiry = expiry;
        this.strike = strike;
        this.symExp = symExp;
    }

    /**
     * Instrument symbol or identifier
     * (Required)
     * 
     */
    @JsonProperty("symb")
    public String getSymb() {
        return symb;
    }

    /**
     * Instrument symbol or identifier
     * (Required)
     * 
     */
    @JsonProperty("symb")
    public void setSymb(String symb) {
        this.symb = symb;
    }

    public MarketDataBar withSymb(String symb) {
        this.symb = symb;
        return this;
    }

    /**
     * Open price
     * (Required)
     * 
     */
    @JsonProperty("op")
    public BigDecimal getOp() {
        return op;
    }

    /**
     * Open price
     * (Required)
     * 
     */
    @JsonProperty("op")
    public void setOp(BigDecimal op) {
        this.op = op;
    }

    public MarketDataBar withOp(BigDecimal op) {
        this.op = op;
        return this;
    }

    /**
     * High price
     * (Required)
     * 
     */
    @JsonProperty("hi")
    public BigDecimal getHi() {
        return hi;
    }

    /**
     * High price
     * (Required)
     * 
     */
    @JsonProperty("hi")
    public void setHi(BigDecimal hi) {
        this.hi = hi;
    }

    public MarketDataBar withHi(BigDecimal hi) {
        this.hi = hi;
        return this;
    }

    /**
     * Low price
     * (Required)
     * 
     */
    @JsonProperty("lo")
    public BigDecimal getLo() {
        return lo;
    }

    /**
     * Low price
     * (Required)
     * 
     */
    @JsonProperty("lo")
    public void setLo(BigDecimal lo) {
        this.lo = lo;
    }

    public MarketDataBar withLo(BigDecimal lo) {
        this.lo = lo;
        return this;
    }

    /**
     * Close price
     * (Required)
     * 
     */
    @JsonProperty("cl")
    public BigDecimal getCl() {
        return cl;
    }

    /**
     * Close price
     * (Required)
     * 
     */
    @JsonProperty("cl")
    public void setCl(BigDecimal cl) {
        this.cl = cl;
    }

    public MarketDataBar withCl(BigDecimal cl) {
        this.cl = cl;
        return this;
    }

    /**
     * Volume traded during this bar
     * (Required)
     * 
     */
    @JsonProperty("vlm")
    public BigDecimal getVlm() {
        return vlm;
    }

    /**
     * Volume traded during this bar
     * (Required)
     * 
     */
    @JsonProperty("vlm")
    public void setVlm(BigDecimal vlm) {
        this.vlm = vlm;
    }

    public MarketDataBar withVlm(BigDecimal vlm) {
        this.vlm = vlm;
        return this;
    }

    /**
     * Volume-weighted average price (optional)
     * 
     */
    @JsonProperty("vwap")
    public BigDecimal getVwap() {
        return vwap;
    }

    /**
     * Volume-weighted average price (optional)
     * 
     */
    @JsonProperty("vwap")
    public void setVwap(BigDecimal vwap) {
        this.vwap = vwap;
    }

    public MarketDataBar withVwap(BigDecimal vwap) {
        this.vwap = vwap;
        return this;
    }

    /**
     * ISO 8601 timestamp representing the bar’s open/close time
     * (Required)
     * 
     */
    @JsonProperty("datetime")
    public Date getDatetime() {
        return datetime;
    }

    /**
     * ISO 8601 timestamp representing the bar’s open/close time
     * (Required)
     * 
     */
    @JsonProperty("datetime")
    public void setDatetime(Date datetime) {
        this.datetime = datetime;
    }

    public MarketDataBar withDatetime(Date datetime) {
        this.datetime = datetime;
        return this;
    }

    /**
     * Number of trades aggregated in this bar (optional)
     * 
     */
    @JsonProperty("count")
    public Long getCount() {
        return count;
    }

    /**
     * Number of trades aggregated in this bar (optional)
     * 
     */
    @JsonProperty("count")
    public void setCount(Long count) {
        this.count = count;
    }

    public MarketDataBar withCount(Long count) {
        this.count = count;
        return this;
    }

    /**
     * Epoch timestamp (milliseconds) when the bar was generated or received
     * (Required)
     * 
     */
    @JsonProperty("timestamp")
    public Long getTimestamp() {
        return timestamp;
    }

    /**
     * Epoch timestamp (milliseconds) when the bar was generated or received
     * (Required)
     * 
     */
    @JsonProperty("timestamp")
    public void setTimestamp(Long timestamp) {
        this.timestamp = timestamp;
    }

    public MarketDataBar withTimestamp(Long timestamp) {
        this.timestamp = timestamp;
        return this;
    }

    /**
     * Trading date for the bar
     * (Required)
     * 
     */
    @JsonProperty("date")
    public String getDate() {
        return date;
    }

    /**
     * Trading date for the bar
     * (Required)
     * 
     */
    @JsonProperty("date")
    public void setDate(String date) {
        this.date = date;
    }

    public MarketDataBar withDate(String date) {
        this.date = date;
        return this;
    }

    /**
     * Option or futures expiry (optional)
     * 
     */
    @JsonProperty("expiry")
    public String getExpiry() {
        return expiry;
    }

    /**
     * Option or futures expiry (optional)
     * 
     */
    @JsonProperty("expiry")
    public void setExpiry(String expiry) {
        this.expiry = expiry;
    }

    public MarketDataBar withExpiry(String expiry) {
        this.expiry = expiry;
        return this;
    }

    /**
     * Option strike price (optional)
     * 
     */
    @JsonProperty("strike")
    public BigDecimal getStrike() {
        return strike;
    }

    /**
     * Option strike price (optional)
     * 
     */
    @JsonProperty("strike")
    public void setStrike(BigDecimal strike) {
        this.strike = strike;
    }

    public MarketDataBar withStrike(BigDecimal strike) {
        this.strike = strike;
        return this;
    }

    /**
     * Symbol + expiry composite identifier (optional)
     * 
     */
    @JsonProperty("symExp")
    public String getSymExp() {
        return symExp;
    }

    /**
     * Symbol + expiry composite identifier (optional)
     * 
     */
    @JsonProperty("symExp")
    public void setSymExp(String symExp) {
        this.symExp = symExp;
    }

    public MarketDataBar withSymExp(String symExp) {
        this.symExp = symExp;
        return this;
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append(MarketDataBar.class.getName()).append('@').append(Integer.toHexString(System.identityHashCode(this))).append('[');
        sb.append("symb");
        sb.append('=');
        sb.append(((this.symb == null)?"<null>":this.symb));
        sb.append(',');
        sb.append("op");
        sb.append('=');
        sb.append(((this.op == null)?"<null>":this.op));
        sb.append(',');
        sb.append("hi");
        sb.append('=');
        sb.append(((this.hi == null)?"<null>":this.hi));
        sb.append(',');
        sb.append("lo");
        sb.append('=');
        sb.append(((this.lo == null)?"<null>":this.lo));
        sb.append(',');
        sb.append("cl");
        sb.append('=');
        sb.append(((this.cl == null)?"<null>":this.cl));
        sb.append(',');
        sb.append("vlm");
        sb.append('=');
        sb.append(((this.vlm == null)?"<null>":this.vlm));
        sb.append(',');
        sb.append("vwap");
        sb.append('=');
        sb.append(((this.vwap == null)?"<null>":this.vwap));
        sb.append(',');
        sb.append("datetime");
        sb.append('=');
        sb.append(((this.datetime == null)?"<null>":this.datetime));
        sb.append(',');
        sb.append("count");
        sb.append('=');
        sb.append(((this.count == null)?"<null>":this.count));
        sb.append(',');
        sb.append("timestamp");
        sb.append('=');
        sb.append(((this.timestamp == null)?"<null>":this.timestamp));
        sb.append(',');
        sb.append("date");
        sb.append('=');
        sb.append(((this.date == null)?"<null>":this.date));
        sb.append(',');
        sb.append("expiry");
        sb.append('=');
        sb.append(((this.expiry == null)?"<null>":this.expiry));
        sb.append(',');
        sb.append("strike");
        sb.append('=');
        sb.append(((this.strike == null)?"<null>":this.strike));
        sb.append(',');
        sb.append("symExp");
        sb.append('=');
        sb.append(((this.symExp == null)?"<null>":this.symExp));
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
        result = ((result* 31)+((this.date == null)? 0 :this.date.hashCode()));
        result = ((result* 31)+((this.op == null)? 0 :this.op.hashCode()));
        result = ((result* 31)+((this.hi == null)? 0 :this.hi.hashCode()));
        result = ((result* 31)+((this.lo == null)? 0 :this.lo.hashCode()));
        result = ((result* 31)+((this.vwap == null)? 0 :this.vwap.hashCode()));
        result = ((result* 31)+((this.strike == null)? 0 :this.strike.hashCode()));
        result = ((result* 31)+((this.count == null)? 0 :this.count.hashCode()));
        result = ((result* 31)+((this.cl == null)? 0 :this.cl.hashCode()));
        result = ((result* 31)+((this.symb == null)? 0 :this.symb.hashCode()));
        result = ((result* 31)+((this.symExp == null)? 0 :this.symExp.hashCode()));
        result = ((result* 31)+((this.datetime == null)? 0 :this.datetime.hashCode()));
        result = ((result* 31)+((this.vlm == null)? 0 :this.vlm.hashCode()));
        result = ((result* 31)+((this.expiry == null)? 0 :this.expiry.hashCode()));
        result = ((result* 31)+((this.timestamp == null)? 0 :this.timestamp.hashCode()));
        return result;
    }

    @Override
    public boolean equals(Object other) {
        if (other == this) {
            return true;
        }
        if ((other instanceof MarketDataBar) == false) {
            return false;
        }
        MarketDataBar rhs = ((MarketDataBar) other);
        return (((((((((((((((this.date == rhs.date)||((this.date!= null)&&this.date.equals(rhs.date)))&&((this.op == rhs.op)||((this.op!= null)&&this.op.equals(rhs.op))))&&((this.hi == rhs.hi)||((this.hi!= null)&&this.hi.equals(rhs.hi))))&&((this.lo == rhs.lo)||((this.lo!= null)&&this.lo.equals(rhs.lo))))&&((this.vwap == rhs.vwap)||((this.vwap!= null)&&this.vwap.equals(rhs.vwap))))&&((this.strike == rhs.strike)||((this.strike!= null)&&this.strike.equals(rhs.strike))))&&((this.count == rhs.count)||((this.count!= null)&&this.count.equals(rhs.count))))&&((this.cl == rhs.cl)||((this.cl!= null)&&this.cl.equals(rhs.cl))))&&((this.symb == rhs.symb)||((this.symb!= null)&&this.symb.equals(rhs.symb))))&&((this.symExp == rhs.symExp)||((this.symExp!= null)&&this.symExp.equals(rhs.symExp))))&&((this.datetime == rhs.datetime)||((this.datetime!= null)&&this.datetime.equals(rhs.datetime))))&&((this.vlm == rhs.vlm)||((this.vlm!= null)&&this.vlm.equals(rhs.vlm))))&&((this.expiry == rhs.expiry)||((this.expiry!= null)&&this.expiry.equals(rhs.expiry))))&&((this.timestamp == rhs.timestamp)||((this.timestamp!= null)&&this.timestamp.equals(rhs.timestamp))));
    }

}
