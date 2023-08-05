/*
 * Common input functions for the fvdetools
 *
 * Copyright (C) 2011-2022, Metz <joachim.metz@gmail.com>
 *
 * Refer to AUTHORS for acknowledgements.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

#if !defined( _FVDETOOLS_INPUT_H )
#define _FVDETOOLS_INPUT_H

#include <common.h>
#include <file_stream.h>
#include <types.h>

#include "fvdetools_libcerror.h"

#if defined( __cplusplus )
extern "C" {
#endif

int fvdetools_prompt_for_password(
     FILE *stream,
     const system_character_t *request_string,
     system_character_t *password,
     size_t password_size,
     libcerror_error_t **error );

#if defined( __cplusplus )
}
#endif

#endif /* !defined( _FVDETOOLS_INPUT_H ) */

