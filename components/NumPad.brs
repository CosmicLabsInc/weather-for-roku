sub init()
    m.keyW = 96
    m.keyH = 54
    m.gapX = 14
    m.gapY = 8
    m.focusRow = 0
    m.focusCol = 0

    m.keyLabels = [
        ["1", "2", "3"]
        ["4", "5", "6"]
        ["7", "8", "9"]
        ["DEL", "0", "GO"]
    ]

    m.keyValues = [
        ["1", "2", "3"]
        ["4", "5", "6"]
        ["7", "8", "9"]
        ["back", "0", "go"]
    ]

    m.backgrounds = []
    m.labels = []

    ' key backgrounds (bottom layer)
    for row = 0 to 3
        rowBg = []
        for col = 0 to 2
            x = col * (m.keyW + m.gapX)
            y = row * (m.keyH + m.gapY)
            bg = m.top.CreateChild("Poster")
            if m.keyValues[row][col] = "go"
                bg.uri = "pkg:/images/ui/key_action.png"
            else
                bg.uri = "pkg:/images/ui/key.png"
            end if
            bg.width = m.keyW
            bg.height = m.keyH
            bg.translation = [x, y]
            rowBg.Push(bg)
        end for
        m.backgrounds.Push(rowBg)
    end for

    ' focus highlight (above backgrounds, below labels)
    m.focus = m.top.CreateChild("Poster")
    m.focus.uri = "pkg:/images/ui/key_focus.png"
    m.focus.width = 116
    m.focus.height = 74

    ' labels on top
    for row = 0 to 3
        rowLabels = []
        for col = 0 to 2
            x = col * (m.keyW + m.gapX)
            y = row * (m.keyH + m.gapY)
            lbl = m.top.CreateChild("Label")
            lbl.width = m.keyW
            lbl.height = m.keyH
            lbl.horizAlign = "center"
            lbl.vertAlign = "center"
            lbl.translation = [x, y]
            val = m.keyValues[row][col]
            if val = "go" or val = "back"
                lbl.font = "font:SmallBoldSystemFont"
            else
                lbl.font = "font:MediumBoldSystemFont"
            end if
            lbl.text = m.keyLabels[row][col]
            rowLabels.Push(lbl)
        end for
        m.labels.Push(rowLabels)
    end for

    updateFocusVisual()
    m.top.focusable = true
    m.top.SetFocus(true)
end sub

function onKeyEvent(key as string, press as boolean) as boolean
    if not press then return false

    if key = "left"
        if m.focusCol > 0
            m.focusCol = m.focusCol - 1
            updateFocusVisual()
        end if
        return true
    else if key = "right"
        if m.focusCol < 2
            m.focusCol = m.focusCol + 1
            updateFocusVisual()
        end if
        return true
    else if key = "up"
        if m.focusRow > 0
            m.focusRow = m.focusRow - 1
            updateFocusVisual()
        end if
        return true
    else if key = "down"
        if m.focusRow < 3
            m.focusRow = m.focusRow + 1
            updateFocusVisual()
        end if
        return true
    else if key = "OK"
        m.top.keyPressed = m.keyValues[m.focusRow][m.focusCol]
        return true
    end if

    return false
end function

sub updateFocusVisual()
    for row = 0 to 3
        for col = 0 to 2
            lbl = m.labels[row][col]
            val = m.keyValues[row][col]
            isFocused = (row = m.focusRow and col = m.focusCol)

            if isFocused
                lbl.color = "0x0B1220FF"
            else if val = "go"
                lbl.color = "0xF8FAFCFF"
            else if val = "back"
                lbl.color = "0x94A3B8FF"
            else
                lbl.color = "0xF1F5F9FF"
            end if
        end for
    end for

    keyX = m.focusCol * (m.keyW + m.gapX)
    keyY = m.focusRow * (m.keyH + m.gapY)
    centerX = keyX + m.keyW / 2
    centerY = keyY + m.keyH / 2
    m.focus.translation = [centerX - m.focus.width / 2, centerY - m.focus.height / 2]
end sub

sub resetFocus()
    m.focusRow = 0
    m.focusCol = 0
    updateFocusVisual()
    m.top.SetFocus(true)
end sub
