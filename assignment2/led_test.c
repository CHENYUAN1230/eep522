#include <gpiod.h> // GPIO
#include <stdio.h>
#include <unistd.h> // use sleep()
/*
| Structure              | Role (Description)                                                                                |
| ---------------------- | ------------------------------------------------------------------------------------------------- |
| `gpiod_chip`           | Represents a GPIO controller exposed by the Linux kernel (e.g., `/dev/gpiochip0`).                |
| `gpiod_line_settings`  | Defines how an individual GPIO line is configured (input/output, bias, active level).             |
| `gpiod_line_config`    | Aggregates the configuration of one or more GPIO lines into a single request.                     |
| `gpiod_request_config` | Specifies metadata about the GPIO request, such as the consumer name.                             |
| `gpiod_line_request`   | Represents an approved GPIO line request, granting exclusive access to the configured GPIO lines. |

*/


int main(void) 
{
    struct gpiod_chip *chip; // GPIO controller
    struct gpiod_line_settings *led_settings, *btn_settings; // two setting for different GPIO Pins
    struct gpiod_line_config *line_cfg; // combine all the setting to a config
    struct gpiod_request_config *req_cfg;
    struct gpiod_line_request *request;

    unsigned int led_line = 17;   // GPIO 17
    unsigned int btn_line = 27;   // GPIO 27

    chip = gpiod_chip_open("/dev/gpiochip0"); // in Linux
    if (!chip) 
    {
        perror("gpiod_chip_open");
        return 1;
    }

    /* LED: output */
    led_settings = gpiod_line_settings_new();
    gpiod_line_settings_set_direction(led_settings, GPIOD_LINE_DIRECTION_OUTPUT); // set led as Output
    gpiod_line_settings_set_output_value(led_settings, GPIOD_LINE_VALUE_INACTIVE); // set led as inactive 

    /* Button: input + pull-up */
    btn_settings = gpiod_line_settings_new();
    gpiod_line_settings_set_direction(btn_settings, GPIOD_LINE_DIRECTION_INPUT); // set button as Input
    gpiod_line_settings_set_bias(btn_settings, GPIOD_LINE_BIAS_PULL_UP); // set button as pull-up, unpress: HIGH, press: LOW

    /* Add all the setting into Config */
    line_cfg = gpiod_line_config_new();
    gpiod_line_config_add_line_settings(line_cfg, &led_line, 1, led_settings);
    gpiod_line_config_add_line_settings(line_cfg, &btn_line, 1, btn_settings);

    /* Say "Hi, Linux, I am button_led the program, I will use GPIO"*/
    req_cfg = gpiod_request_config_new();
    gpiod_request_config_set_consumer(req_cfg, "button_led");

    /* Ask Linux to borrow GPIO*/
    request = gpiod_chip_request_lines(chip, req_cfg, line_cfg);
    if (!request) // check 1. whether other program use GPIO 2. the authority
    {
        perror("gpiod_chip_request_lines");
        return 1;
    }

    printf("Press the button to turn LED ON\n");

    while (1) 
    {
        int btn = gpiod_line_request_get_value(request, btn_line);

        if (btn == 0) 
        {
            /* button pressed */
            gpiod_line_request_set_value(request, led_line, GPIOD_LINE_VALUE_ACTIVE);
        } 
        else 
        {
            /* button released */
            gpiod_line_request_set_value(request, led_line, GPIOD_LINE_VALUE_INACTIVE);
        }

        usleep(10000); // 10 ms polling (rest a bit)
    }
}
