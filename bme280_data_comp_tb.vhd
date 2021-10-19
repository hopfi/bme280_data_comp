----------------------------------------------------------------------------------
-- Name: Daniel Hopfinger
-- Date: 05.08.2021
-- Module: bme280_data_comp_tb.vhd
-- Description:
-- Testbench to bme280_data_comp module.
-- Input and Output to module is created by a python script based on the formulars in the datasheet to the BME280 sensor.
--
-- History:
-- Version  | Date       | Information
-- ----------------------------------------
--  0.0.1   | 05.08.2021 | Initial version.
--
----------------------------------------------------------------------------------

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use std.textio.all;

library gen;

entity bme280_data_comp_tb is
end bme280_data_comp_tb;

architecture sim of bme280_data_comp_tb is

    constant C_CLK_PERIOD : time := 10 ns;

    signal clk : std_logic := '1';
    signal rst : std_logic := '1';

    signal inputData   : std_logic_vector(31 downto 0);
    signal adc_T       : std_logic_vector(31 downto 0);
    signal adc_P       : std_logic_vector(31 downto 0);
    signal adc_H       : std_logic_vector(31 downto 0);
    signal adc_vld     : std_logic;
    signal temperature : std_logic_vector(31 downto 0);
    signal pressure    : std_logic_vector(31 downto 0);
    signal humidity    : std_logic_vector(31 downto 0);
    signal valid       : std_logic;

    signal temp_exp : std_logic_vector(31 downto 0);
    signal pres_exp : std_logic_vector(31 downto 0);
    signal hum_exp : std_logic_vector(31 downto 0);
    signal temp_res : std_logic_vector(31 downto 0);
    signal pres_res : std_logic_vector(31 downto 0);
    signal hum_res : std_logic_vector(31 downto 0);


begin

    clk <= not clk after C_CLK_PERIOD / 2;
    rst <= '0' after 10 * C_CLK_PERIOD;

    master_proc : process
        file fh           : text open read_mode is "./stimData.txt";
        variable var_line : line;
        variable var_data : std_logic_vector(31 downto 0);
        variable var_char : character;
    begin

        if rst = '1' then
            wait until rst = '0';
            adc_vld <= '0';
        end if;
        wait for 50 * C_CLK_PERIOD;
        wait until rising_edge(clk);

        while not endfile(fh) loop

            readline(fh, var_line);
            read(var_line, var_data);
            inputData <= var_data;
            read(var_line, var_char);
            read(var_line, var_data);
            --temp_exp <= std_logic_vector((not var_data) + x"0000_0001");
            temp_exp <= var_data;
            read(var_line, var_char);
            read(var_line, var_data);
            pres_exp <= var_data;
            read(var_line, var_char);
            read(var_line, var_data);
            hum_exp <= var_data;
            
            adc_vld <= '1';
            wait for 1*C_CLK_PERIOD;
            adc_vld <= '0';
            wait for 1*C_CLK_PERIOD;
            assert valid = '0'
            report "Output valid signal was not reset when input valid was received!"
            severity failure;

            wait until rising_edge(valid);

            assert temperature = temp_exp
            report  "Calculated temperature does not match expected temperature" & lf &
                    "Expected: " & integer'image(to_integer(signed(temp_exp))) & lf &
                    "Acutal: " & integer'image(to_integer(signed(temperature)))
            severity failure;
            assert pressure = pres_exp
            report  "Calculated temperature does not match expected temperature" & lf &
                    "Expected: " & integer'image(to_integer(signed(pres_exp))) & lf &
                    "Acutal: " & integer'image(to_integer(signed(pressure)))
            severity failure;
            --assert humidity = hum_exp
            --report  "Calculated temperature does not match expected temperature" & lf &
            --        "Expected: " & integer'image(to_integer(signed(hum_exp))) & lf &
            --        "Acutal: " & integer'image(to_integer(signed(humidity)))
            --severity failure;

            wait for 5 * C_CLK_PERIOD;

        end loop;

        wait for 100 * C_CLK_PERIOD;

        std.env.stop(0);

    end process master_proc;

    data_comp : entity gen.bme280_data_comp(rtl)
    port map (
        i_clk         => clk,
        i_rst         => rst,
        i_adc_T       => adc_T,
        i_adc_P       => adc_P,
        i_adc_H       => adc_H,
        i_adc_vld     => adc_vld,
        o_temperature => temperature,
        o_pressure    => pressure,
        o_humidity    => humidity,
        o_valid       => valid
    );
    adc_T <= inputData;
    adc_P <= inputData;
    adc_H <= inputData;

end sim;
