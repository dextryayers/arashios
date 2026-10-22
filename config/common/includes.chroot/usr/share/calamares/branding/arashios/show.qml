/*
 * ArashiOS installer slideshow.
 * The slideshow is text only so it renders without extra image assets and
 * keeps the installer theme consistent with the Kage palette.
 */
import QtQuick 2.0
import SlideCounter 1.0

Slide {
    id: root
    title: qsTr("Menyiapkan ArashiOS")
    subtitle: qsTr("Tidak ada data yang dikirim ke server mana pun.")
    logo: "file:///usr/share/icons/hicolor/scalable/apps/arashios.svg"
    Component.onCompleted: {
        // Nothing to start. The slideshow is static by design.
    }
}
