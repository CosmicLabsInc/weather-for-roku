sub init()
    m.zipScreen = m.top.FindNode("zipScreen")
    m.loadingScreen = m.top.FindNode("loadingScreen")
    m.forecastScreen = m.top.FindNode("forecastScreen")
    m.forecastRow = m.top.FindNode("forecastRow")
    m.statusLabel = m.top.FindNode("statusLabel")
    m.locationLabel = m.top.FindNode("locationLabel")
    m.zipLabel = m.top.FindNode("zipLabel")
    m.numPad = m.top.FindNode("numPad")
    m.loadTimer = m.top.FindNode("loadTimer")

    m.statusHint = "Use the arrows and OK. Select GO when done."

    m.digitLabels = [
        m.top.FindNode("digit0")
        m.top.FindNode("digit1")
        m.top.FindNode("digit2")
        m.top.FindNode("digit3")
        m.top.FindNode("digit4")
    ]

    m.digitBoxes = [
        m.top.FindNode("digitBox0")
        m.top.FindNode("digitBox1")
        m.top.FindNode("digitBox2")
        m.top.FindNode("digitBox3")
        m.top.FindNode("digitBox4")
    ]

    m.digitActives = [
        m.top.FindNode("digitActive0")
        m.top.FindNode("digitActive1")
        m.top.FindNode("digitActive2")
        m.top.FindNode("digitActive3")
        m.top.FindNode("digitActive4")
    ]

    m.digits = ""
    m.screen = "zip"
    m.weatherTask = invalid

    m.numPad.observeField("keyPressed", "onNumPadKey")
    m.loadTimer.observeField("fire", "onLoadTimeout")
    m.top.SetFocus(true)

    savedZip = getSavedZip()
    if savedZip <> invalid and Len(savedZip) = 5
        m.digits = savedZip
        updateDigitDisplay()
        fetchForecast(savedZip)
    else
        showScreen("zip")
        updateDigitDisplay()
        focusNumPad()
    end if
end sub

function getSavedZip() as dynamic
    section = CreateObject("roRegistrySection", "weather")
    if section.Exists("zip")
        return section.Read("zip")
    end if
    return invalid
end function

sub saveZip(zip as string)
    section = CreateObject("roRegistrySection", "weather")
    section.Write("zip", zip)
    section.Flush()
end sub

function onKeyEvent(key as string, press as boolean) as boolean
    if not press then return false

    if m.screen = "forecast"
        if key = "options"
            resetToZip()
            return true
        end if
    end if

    return false
end function

sub onNumPadKey()
    key = m.numPad.keyPressed
    if key = invalid or key = "" then return

    if key = "back"
        if Len(m.digits) > 0
            m.digits = Left(m.digits, Len(m.digits) - 1)
            updateDigitDisplay()
            clearError()
        end if
        focusNumPad()
        return
    end if

    if key = "go"
        if Len(m.digits) = 5
            fetchForecast(m.digits)
        else
            showError("Enter all 5 digits, then select GO.")
        end if
        focusNumPad()
        return
    end if

    if Len(m.digits) < 5
        m.digits = m.digits + key
        updateDigitDisplay()
        clearError()
    end if

    focusNumPad()
end sub

sub showError(message as string)
    m.statusLabel.text = message
    m.statusLabel.color = "0xFCA5A5FF"
end sub

sub clearError()
    m.statusLabel.text = m.statusHint
    m.statusLabel.color = "0x64748BFF"
end sub

sub focusNumPad()
    m.numPad.callFunc("resetFocus")
    m.numPad.SetFocus(true)
end sub

sub updateDigitDisplay()
    for i = 0 to 4
        if i < Len(m.digits)
            m.digitLabels[i].text = Mid(m.digits, i + 1, 1)
            m.digitBoxes[i].uri = "pkg:/images/ui/digit_filled.png"
            m.digitActives[i].visible = false
        else
            m.digitLabels[i].text = ""
            m.digitBoxes[i].uri = "pkg:/images/ui/digit.png"
            m.digitActives[i].visible = (i = Len(m.digits))
        end if
    end for
end sub

sub fetchForecast(zip as string)
    clearError()
    showScreen("loading")

    if m.weatherTask <> invalid
        m.weatherTask.unobserveField("content")
        m.weatherTask.unobserveField("error")
        m.weatherTask.control = "STOP"
    end if

    m.weatherTask = CreateObject("roSGNode", "WeatherTask")
    m.weatherTask.zip = zip
    m.weatherTask.observeField("content", "onForecastLoaded")
    m.weatherTask.observeField("error", "onForecastError")
    m.weatherTask.control = "RUN"

    m.loadTimer.control = "start"
end sub

sub onLoadTimeout()
    if m.screen <> "loading" then return
    cleanupWeatherTask()
    showError("Request timed out. Check your internet connection.")
    showScreen("zip")
    focusNumPad()
end sub

sub cleanupWeatherTask()
    m.loadTimer.control = "stop"
    if m.weatherTask = invalid then return
    m.weatherTask.unobserveField("content")
    m.weatherTask.unobserveField("error")
end sub

sub onForecastLoaded()
    content = m.weatherTask.content
    if content = invalid then return

    cleanupWeatherTask()

    saveZip(content.zip)
    renderForecast(content)
    showScreen("forecast")
end sub

sub onForecastError()
    errorMessage = m.weatherTask.error
    if errorMessage = invalid or errorMessage = "" then return

    cleanupWeatherTask()

    showError(errorMessage)
    showScreen("zip")
    focusNumPad()
end sub

sub renderForecast(content as object)
    m.locationLabel.text = content.place
    m.zipLabel.text = "ZIP " + content.zip + "   •   7-Day Forecast"

    childCount = m.forecastRow.getChildCount()
    if childCount > 0
        m.forecastRow.removeChildrenIndex(childCount, 0)
    end if

    dayCount = content.days.Count()
    cardWidth = 150
    gap = 8
    totalWidth = dayCount * cardWidth + (dayCount - 1) * gap
    startX = Int((1280 - totalWidth) / 2)

    i = 0
    for each dayData in content.days
        card = CreateObject("roSGNode", "DayCard")
        card.dayData = dayData
        card.translation = [startX + i * (cardWidth + gap), 0]
        m.forecastRow.AppendChild(card)
        i = i + 1
    end for
end sub

sub resetToZip()
    m.digits = ""
    updateDigitDisplay()
    clearError()
    showScreen("zip")
    focusNumPad()
end sub

sub showScreen(name as string)
    m.screen = name
    m.zipScreen.visible = (name = "zip")
    m.loadingScreen.visible = (name = "loading")
    m.forecastScreen.visible = (name = "forecast")
end sub
