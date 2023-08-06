// -*- coding: utf-8 -*-
// Header file generated automatically by cslug.
// Do not modify this file directly as your changes will be overwritten.

#ifndef ENDIANS_H
#define ENDIANS_H

#include <stdbool.h>
#include "_endian_typedefs.h"

// endians.c
bool is_big_endian();
uint8_t swap_endian_8(uint8_t x);
uint16_t swap_endian_16(uint16_t x);
uint32_t swap_endian_32(uint32_t x);
uint64_t swap_endian_64(uint64_t x);
void write_8 (uint64_t x, void * out);
void write_16(uint64_t x, void * out);
void write_32(uint64_t x, void * out);
void write_64(uint64_t x, void * out);
void write_swap_8 (uint64_t x, void * out);
void write_swap_16(uint64_t x, void * out);
void write_swap_32(uint64_t x, void * out);
void write_swap_64(uint64_t x, void * out);
IntWrite choose_int_write(int power, bool big_endian);
uint64_t read_8 (void * x);
uint64_t read_16(void * x);
uint64_t read_32(void * x);
uint64_t read_64(void * x);
uint64_t read_swap_8 (void * x);
uint64_t read_swap_16(void * x);
uint64_t read_swap_32(void * x);
uint64_t read_swap_64(void * x);
IntRead choose_int_read(int power, bool big_endian);
void * _choose_int_read_write(int power, bool big_endian, void ** list);

#endif
