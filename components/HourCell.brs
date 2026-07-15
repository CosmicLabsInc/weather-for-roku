sub init()
    m.timeLabel = m.top.FindNode("timeLabel")
    m.hourIcon = m.top.FindNode("hourIcon")
    m.tempLabel = m.top.FindNode("tempLabel")
    m.condLabel = m.top.FindNode("condLabel")
end sub

sub onHourDataChanged()
    data = m.top.hourData
    if data = invalid then return

    m.timeLabel.text = data.timeLabel
    m.tempLabel.text = data.temp + "°"
    m.condLabel.text = data.condition
    m.hourIcon.uri = data.iconUri

    if data.isNow = true
        m.timeLabel.color = "0x7DD3FCFF"
    else
        m.timeLabel.color = "0xF8FAFCFF"
    end if
end sub
