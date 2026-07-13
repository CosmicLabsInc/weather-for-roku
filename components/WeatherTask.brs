sub init()
    m.top.functionName = "loadForecast"
end sub

' Identify the app to NWS. Replace the contact with your real email/site.
function userAgent() as string
    return "WeatherRokuApp/1.0 (https://github.com/weather-roku; contact@example.com)"
end function

sub loadForecast()
    zip = m.top.zip
    if zip = invalid or Len(zip) <> 5
        m.top.error = "Please enter a valid 5-digit US zip code."
        return
    end if

    loc = lookupZip(zip)
    if loc = invalid
        m.top.error = "ZIP code not found. Try another US ZIP code."
        return
    end if

    ' 1) Resolve the NWS grid point + place name for these coordinates.
    pointsUrl = "https://api.weather.gov/points/" + loc.lat + "," + loc.lon
    pj = fetchJson(pointsUrl)
    if pj = invalid or pj.properties = invalid
        m.top.error = "Couldn't load the forecast. Please try again."
        return
    end if

    props = pj.properties
    forecastUrl = props.forecast
    if forecastUrl = invalid or forecastUrl = ""
        m.top.error = "Forecast isn't available for this location."
        return
    end if
    placeName = buildPlaceName(props)

    ' 2) Fetch the daily/nightly forecast periods.
    fj = fetchJson(forecastUrl)
    if fj = invalid or fj.properties = invalid or fj.properties.periods = invalid
        m.top.error = "Couldn't load the forecast. Please try again."
        return
    end if

    periods = fj.properties.periods
    if periods.Count() = 0
        m.top.error = "No forecast data available for this location."
        return
    end if

    days = buildDays(periods)
    if days.Count() = 0
        m.top.error = "No forecast data available for this location."
        return
    end if

    m.top.content = {
        zip: zip
        place: placeName
        days: days
    }
end sub

' Collapse NWS day/night periods into up to 7 daily high/low entries.
function buildDays(periods as object) as object
    byDate = {}
    order = []

    for each p in periods
        st = p.startTime
        if st <> invalid and Len(st) >= 10
            dkey = Mid(st, 1, 10)
            entry = byDate[dkey]
            if entry = invalid
                entry = { date: dkey, high: invalid, low: invalid, cond: invalid, precip: invalid }
                byDate[dkey] = entry
                order.Push(dkey)
            end if

            pop = invalid
            if p.probabilityOfPrecipitation <> invalid
                pop = p.probabilityOfPrecipitation.value
            end if

            if p.isDaytime = true
                entry.high = p.temperature
                entry.cond = p.shortForecast
                if pop <> invalid then entry.precip = pop
            else
                entry.low = p.temperature
                if entry.cond = invalid then entry.cond = p.shortForecast
                if entry.precip = invalid and pop <> invalid then entry.precip = pop
            end if
        end if
    end for

    days = []
    count = 0
    for each dkey in order
        if count >= 7 then exit for
        e = byDate[dkey]

        ' Late-evening launches only have "Tonight" (a low) for the first day;
        ' promote it into the prominent slot so the card shows a real number.
        high = e.high
        low = e.low
        if high = invalid and low <> invalid
            high = low
            low = invalid
        end if

        cls = classify(e.cond)
        days.Push({
            dayLabel: formatDayLabel(dkey, count = 0)
            isToday: (count = 0)
            condition: cls.label
            iconUri: cls.icon
            high: intStr(high)
            low: intStr(low)
            precip: intStr(e.precip)
        })
        count = count + 1
    end for

    return days
end function

' Binary search the bundled Census ZCTA table (fixed-width, zip-sorted).
' Record: zip(5) + lat(9) + lon(10) = 24 bytes, no delimiters.
function lookupZip(zip as string) as object
    data = ReadAsciiFile("pkg:/data/zips.dat")
    if data = invalid or Len(data) = 0 then return invalid

    recW = 24
    n = Int(Len(data) / recW)
    target = zip.ToInt()

    lo = 0
    hi = n - 1
    for pass = 0 to 40
        if lo > hi then exit for
        midx = Int((lo + hi) / 2)
        off = midx * recW
        z = Mid(data, off + 1, 5).ToInt()
        if z = target
            return { lat: Mid(data, off + 6, 9).Trim(), lon: Mid(data, off + 15, 10).Trim() }
        end if
        if z < target
            lo = midx + 1
        else
            hi = midx - 1
        end if
    end for

    return invalid
end function

function fetchJson(url as string) as dynamic
    request = CreateObject("roUrlTransfer")
    request.SetUrl(url)
    request.SetCertificatesFile("common:/certs/ca-bundle.crt")
    request.InitClientCertificates()
    request.AddHeader("User-Agent", userAgent())
    request.AddHeader("Accept", "application/geo+json")
    request.SetRequest("GET")

    response = request.GetToString()
    if response = invalid or response = "" then return invalid

    return ParseJson(response)
end function

function intStr(value as dynamic) as string
    if value = invalid then return "--"
    return Str(Cint(value)).Trim()
end function

function buildPlaceName(props as object) as string
    rel = props.relativeLocation
    if rel <> invalid and rel.properties <> invalid
        p = rel.properties
        city = p.city
        state = p.state
        if city <> invalid and city <> ""
            if state <> invalid and state <> ""
                return city + ", " + state
            end if
            return city
        end if
    end if
    return "Your Forecast"
end function

' Build a condition result (kept out of single-line if/then to satisfy the parser).
function cond(label as string, file as string) as object
    return { label: label, icon: "pkg:/images/weather/" + file }
end function

' True if any comma-separated needle appears in t.
function hasAny(t as string, needles as string) as boolean
    for each s in needles.Split(",")
        if Instr(1, t, s) > 0 then return true
    end for
    return false
end function

' Map an NWS shortForecast string to our condition label + bundled icon.
function classify(text as dynamic) as object
    if text = invalid then return cond("Cloudy", "cloudy.png")
    t = LCase(text)

    if hasAny(t, "thunder") then return cond("Storms", "thunderstorm.png")
    if hasAny(t, "snow,flurr,sleet,ice,wintry,blizzard,freezing") then return cond("Snow", "snow.png")
    if hasAny(t, "drizzle") then return cond("Drizzle", "drizzle.png")
    if hasAny(t, "shower") then return cond("Showers", "showers.png")
    if hasAny(t, "rain") then return cond("Rain", "rain.png")
    if hasAny(t, "fog,haze,mist") then return cond("Foggy", "fog.png")
    if hasAny(t, "partly sunny,partly cloudy,mostly cloudy") then return cond("Partly Cloudy", "partly_cloudy.png")
    if hasAny(t, "sunny,clear") then return cond("Sunny", "clear.png")
    if hasAny(t, "cloud,overcast") then return cond("Cloudy", "cloudy.png")

    return cond("Cloudy", "cloudy.png")
end function

function formatDayLabel(dateStr as dynamic, isToday as boolean) as string
    if isToday then return "Today"
    if dateStr = invalid or Len(dateStr) < 10 then return "--"

    parts = dateStr.Split("-")
    if parts.Count() < 3 then return dateStr

    year = parts[0].ToInt()
    month = parts[1].ToInt()
    day = parts[2].ToInt()

    dayNames = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    return dayNames[dayOfWeek(year, month, day)]
end function

' Zeller-based day of week, returns 0=Sun .. 6=Sat
function dayOfWeek(year as integer, month as integer, day as integer) as integer
    y = year
    m = month
    if m < 3
        m = m + 12
        y = y - 1
    end if

    k = y mod 100
    j = Int(y / 100)
    h = (day + Int((13 * (m + 1)) / 5) + k + Int(k / 4) + Int(j / 4) + 5 * j) mod 7

    ' Zeller: 0=Sat,1=Sun,...,6=Fri -> convert to 0=Sun..6=Sat
    map = [6, 0, 1, 2, 3, 4, 5]
    return map[h]
end function
