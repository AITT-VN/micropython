// This configuration is for a generic ESP32C3 board with 4MiB (or more) of flash.

#define MICROPY_HW_BOARD_NAME               "YOLO NODE"
#define MICROPY_HW_MCU_NAME                 "ESP32-C3FH4"
#define MICROPY_PY_NETWORK_HOSTNAME_DEFAULT "yolo-node"

#define MICROPY_HW_ENABLE_SDCARD            (0)
#define MICROPY_PY_MACHINE_I2S              (0)

// Enable UART REPL for modules that have an external USB-UART and don't use native USB.
#define MICROPY_HW_ENABLE_UART_REPL         (0)

#define MICROPY_HW_I2C0_SCL                 (6)
#define MICROPY_HW_I2C0_SDA                 (5)
