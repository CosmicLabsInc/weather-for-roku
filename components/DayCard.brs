sub init()
    m.cardBg = m.top.FindNode("cardBg")
    m.dayLabel = m.top.FindNode("dayLabel")
    m.weatherIcon = m.top.FindNode("weatherIcon")
    m.conditionLabel = m.top.FindNode("conditionLabel")
    m.highLabel = m.top.FindNode("highLabel")
    m.lowLabel = m.top.FindNode("lowLabel")
    m.precipLabel = m.top.FindNode("precipLabel")
end sub

sub onDayDataChanged()
    data = m.top.dayData
    if data = invalid then return

    isToday = (data.isToday = true)

    m.dayLabel.text = data.dayLabel
    m.conditionLabel.text = data.condition
    m.highLabel.text = data.high + "°"
    m.lowLabel.text = data.low + "°"
    m.weatherIcon.uri = data.iconUri

    if data.precip <> invalid and data.precip <> "--"
        m.precipLabel.text = data.precip + "% rain"
    else
        m.precipLabel.text = "0% rain"
    end if

    if isToday
        m.cardBg.uri = "pkg:/images/ui/card_today.png"
        m.dayLabel.color = "0x7DD3FCFF"
    else
        m.cardBg.uri = "pkg:/images/ui/card.png"
        m.dayLabel.color = "0xF8FAFCFF"
    end if
end sub
