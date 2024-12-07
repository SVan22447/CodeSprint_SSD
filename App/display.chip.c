

#include "wokwi-api.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define DISPLAY_WIDTH 400
#define DISPLAY_HEIGHT 300
#define BUFFER_SIZE (DISPLAY_WIDTH * DISPLAY_HEIGHT / 8)

typedef struct {
  pin_t cs_pin;
  uint32_t spi;
  uint8_t spi_buffer[BUFFER_SIZE];
  buffer_t framebuffer;
  uint32_t width;
  uint32_t height;
  uint32_t bytes_received;
} chip_state_t;

static void chip_pin_change(void *user_data, pin_t pin, uint32_t value);
static void chip_spi_done(void *user_data, uint8_t *buffer, uint32_t count);

void chip_init() {
  chip_state_t *chip = malloc(sizeof(chip_state_t));
  
  chip->cs_pin = pin_init("CS", INPUT_PULLUP);

  const pin_watch_config_t watch_config = {
    .edge = BOTH,
    .pin_change = chip_pin_change,
    .user_data = chip,
  };
  pin_watch(chip->cs_pin, &watch_config);

  const spi_config_t spi_config = {
    .sck = pin_init("SCK", INPUT),
    .mosi = pin_init("MOSI", INPUT),
    .miso = pin_init("MISO", OUTPUT),
    .done = chip_spi_done,
    .user_data = chip,
  };
  chip->spi = spi_init(&spi_config);

  chip->framebuffer = framebuffer_init(&chip->width, &chip->height);
  chip->bytes_received = 0;

  printf("Framebuffer SPI Display initialized. Width: %d, Height: %d\n", DISPLAY_WIDTH, DISPLAY_HEIGHT);
}

void update_display(chip_state_t *chip) {
  printf("update display\n");
  // for (int y = 0; y < DISPLAY_HEIGHT; y++) {
  for (int y = DISPLAY_WIDTH - 1; y >= 0; y--) {
    for (int x = DISPLAY_HEIGHT - 1; x >= 0; x--) {
    // for (int x = 0; x < DISPLAY_HEIGHT; x++) {
      int byte_index = ((DISPLAY_HEIGHT - x) * DISPLAY_WIDTH + y) / 8;
      int bit_index = ((DISPLAY_HEIGHT - x) * DISPLAY_WIDTH + y) % 8;
      uint8_t pixel = (chip->spi_buffer[byte_index] & (1 << (7 - bit_index))) ? 0xFF : 0x00;
      uint32_t rgba = (pixel << 24) | (pixel << 16) | (pixel << 8) | 0xFF;
      buffer_write(chip->framebuffer, (y * chip->width + x) * 4, &rgba, sizeof(rgba));
    }
  }
}

void chip_pin_change(void *user_data, pin_t pin, uint32_t value) {
  chip_state_t *chip = (chip_state_t*)user_data;
  if (pin == chip->cs_pin) {
    if (value == LOW) {
      printf("SPI chip selected\n");
      chip->bytes_received = 0;
      spi_start(chip->spi, chip->spi_buffer, 1);
    } else {
      printf("SPI chip deselected %d of %d\n", chip->bytes_received, BUFFER_SIZE);
      
      if (chip->bytes_received == BUFFER_SIZE) {
        update_display(chip);
      }
      spi_stop(chip->spi);
    }
  }
}

void chip_spi_done(void *user_data, uint8_t *buffer, uint32_t count) {
  chip_state_t *chip = (chip_state_t*)user_data;
  if (!count) {
    return;
  }

  chip->bytes_received += count;

  if (pin_read(chip->cs_pin) == LOW && chip->bytes_received < BUFFER_SIZE) {
    spi_start(chip->spi, &chip->spi_buffer[chip->bytes_received], 1);
  }
}