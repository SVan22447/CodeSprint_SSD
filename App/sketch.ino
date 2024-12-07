#include <SPI.h>
#include <Adafruit_GFX.h>
#include <Fonts/FreeMonoBold9pt7b.h>
#include <Fonts/FreeSansBold9pt7b.h>
#include "qrcode.h"


#define SCREEN_WIDTH 400
#define SCREEN_HEIGHT 300
#define BUFFER_SIZE (SCREEN_WIDTH * SCREEN_HEIGHT / 8)
#define CS_PIN 10

GFXcanvas1 display(SCREEN_WIDTH, SCREEN_HEIGHT);


void drawQRCode(esp_qrcode_handle_t qrcode) {
    int qr_size = esp_qrcode_get_size(qrcode);
    int scale = min(SCREEN_WIDTH, SCREEN_HEIGHT) / qr_size;
    int qr_x = (SCREEN_HEIGHT - (qr_size * scale))/2;
    int qr_y = (SCREEN_WIDTH - (qr_size * scale))/2;

    for (int y = 0; y < qr_size; y++) {
        for (int x = 0; x < qr_size; x++) {
            if (esp_qrcode_get_module(qrcode, x, y)) {
                display.fillRect(qr_x + x * scale, qr_y + y * scale, scale, scale, 1);
            }
        }
    }
}

void setup() {
    Serial.begin(115200);
    SPI.begin();
    pinMode(CS_PIN, OUTPUT);
    digitalWrite(CS_PIN, HIGH);

    // Clear display
    display.setRotation(3);
    display.fillScreen(0);
    // display.setTextSize(1);
    // display.setTextColor(1);

    esp_qrcode_config_t cfg = ESP_QRCODE_CONFIG_DEFAULT();
    cfg.display_func = drawQRCode;
    cfg.max_qrcode_version = 8;  // Adjust as needed
    cfg.qrcode_ecc_level = ESP_QRCODE_ECC_LOW;

    // Generate QR Code
    const char* message = "https://www.youtube.com/watch?v=dQw4w9WgXcQ";
    esp_err_t ret = esp_qrcode_generate(&cfg, message);
    if (ret != ESP_OK) {
        Serial.println("Failed to generate QR code");
        return;
    }


    display.setCursor(10, SCREEN_WIDTH);

    // Transmit buffer to the framebuffer chip
    digitalWrite(CS_PIN, LOW);
    SPI.beginTransaction(SPISettings(1000000, MSBFIRST, SPI_MODE0));
    SPI.transfer(display.getBuffer(), BUFFER_SIZE);
    SPI.endTransaction();
    digitalWrite(CS_PIN, HIGH);

    Serial.println("Display updated");
}

void loop() {
    // Nothing to do in the loop for this demo
}