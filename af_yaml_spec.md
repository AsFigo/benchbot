# YAML Configuration for VHDL designs
# Table of Contents

1. [Introduction to Using YAML for VHDL Design Documentation](#introduction-to-using-yaml-for-vhdl-design-documentation)
    - [Why Use YAML for VHDL Documentation?](#why-use-yaml-for-vhdl-documentation)
    - [Documenting VHDL Design Interfaces with YAML](#documenting-vhdl-design-interfaces-with-yaml)
        - [Key Components](#key-components)
        - [Explanation of Key/Value Pairs](#explanation-of-key-value-pairs)
        - [Benefits](#benefits)

2. [Example YAML File](#example-yaml-file)
3. [Key/Value Pairs Explanation](#key-value-pairs-explanation)
    - [entity](#entity)
    - [libraries](#libraries)
    - [ports](#ports)
        - [Port Details](#port-details)

# Introduction to Using YAML for VHDL Design Documentation

YAML (YAML Ain't Markup Language) is a human-readable data serialization standard that is commonly used for configuration files. It is particularly well-suited for documenting VHDL (VHSIC Hardware Description Language) designs, especially at the interface level. By using YAML, you can create a structured, easy-to-read representation of your VHDL entity interfaces, including details about ports, libraries, and other configurations.

## Why Use YAML for VHDL Documentation?

1. **Readability**: YAML's syntax is designed to be easy to read and write, making it ideal for documenting complex VHDL designs.
2. **Structure**: YAML provides a clear and hierarchical structure, which helps in organizing VHDL design components and their attributes.
3. **Tool Integration**: YAML is supported by many tools and can be easily parsed and converted into other formats for various applications.

## Documenting VHDL Design Interfaces with YAML

When documenting VHDL designs using YAML, you typically describe the entity, the libraries it depends on, and the ports it uses. Here is a basic outline of what such a YAML file might include:

### Key Components

- **Entity**: The name of the VHDL entity.
- **Libraries**: The VHDL libraries required for the entity.
- **Ports**: A list of ports, each with attributes like direction, kind, name, type, and width.


### Explanation of Key/Value Pairs

- **entity**: Represents the name of the VHDL entity.
- **libraries**: Contains the VHDL library dependencies and file paths required for the entity.
- **ports**: Defines a list of ports used in the VHDL entity, each described with several sub-keys:
  - **pDir**: Direction of the port (`in` or `out`).
  - **pKind**: Type of the port (`clk`, `rst`, `port`).
  - **pName**: Name of the port.
  - **pType**: Data type of the port (`std_logic`, `std_logic_vector`).
  - **pWidth**: Width of the port.

### Benefits

Using YAML for VHDL documentation at the interface level provides a clear, organized, and accessible format for describing the design, facilitating better understanding, communication, and maintenance of VHDL projects.



# Example YAML File

```yaml
entity: af_up_dn_counter
libraries: '# DUT file: ../examples/af_ud_counter/dut_src/af_up_dn_counter.vhdl

  library ieee;

  use ieee.std_logic_1164.all;

  use ieee.std_logic_unsigned.all;

  use ieee.numeric_std.all;

  use std.textio.all;

  '
ports:
- pDir: in
  pKind: clk
  pName: i_clk
  pType: std_logic
  pWidth: 1
- pDir: in
  pKind: rst
  pName: i_rst_n
  pType: std_logic
  pWidth: 1
- pDir: in
  pKind: port
  pName: i_up_or_down
  pType: std_logic
  pWidth: 1
- pDir: out
  pKind: port
  pName: o_count
  pType: std_logic_vector
  pWidth: 8
```

## Key/Value Pairs Explanation

### `entity`

- **`entity`**: Represents the name of the VHDL entity.
  - **Type**: `string`
  - **Example**: `af_up_dn_counter`

### `libraries`

- **`libraries`**: Contains the VHDL library dependencies and file paths required for the entity.
  - **Type**: `string`
  - **Example**:
    ```yaml
    '# DUT file: ../examples/af_ud_counter/dut_src/af_up_dn_counter.vhdl

    library ieee;

    use ieee.std_logic_1164.all;

    use ieee.std_logic_unsigned.all;

    use ieee.numeric_std.all;

    use std.textio.all;

    '
    ```

### `ports`

- **`ports`**: Defines a list of ports used in the VHDL entity. Each port contains several sub-keys:

  - **`pDir`**: Represents the direction of the port.
    - **Type**: `string`
    - **Values**: `in`, `out`
    - **Example**: `in`

  - **`pKind`**: Indicates the kind of port, such as clock, reset, or regular port.
    - **Type**: `string`
    - **Values**: `clk`, `rst`, `port`
    - **Example**: `clk`

  - **`pName`**: The name of the port, typically prefixed with `i_` for inputs and `o_` for outputs.
    - **Type**: `string`
    - **Example**: `i_clk`

  - **`pType`**: The data type of the port, such as `std_logic` or `std_logic_vector`.
    - **Type**: `string`
    - **Example**: `std_logic`

  - **`pWidth`**: The width of the port, indicating how many bits the port contains.
    - **Type**: `integer`
    - **Example**: `1`

#### Port Details

1. **Clock Port**
   - **`pDir`**: `in`
   - **`pKind`**: `clk`
   - **`pName`**: `i_clk`
   - **`pType`**: `std_logic`
   - **`pWidth`**: `1`

2. **Reset Port**
   - **`pDir`**: `in`
   - **`pKind`**: `rst`
   - **`pName`**: `i_rst_n`
   - **`pType**: `std_logic`
   - **`pWidth`**: `1`

3. **Direction Control Port**
   - **`pDir`**: `in`
   - **`pKind`**: `port`
   - **`pName`**: `i_up_or_down`
   - **

`pType**: `std_logic`
   - **`pWidth`**: `1`

4. **Count Output Port**
   - **`pDir`**: `out`
   - **`pKind`**: `port`
   - **`pName`**: `o_count`
   - **`pType**: `std_logic_vector`
   - **`pWidth`**: `8`

