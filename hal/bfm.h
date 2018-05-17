#ifndef __BFM_H__
#define __BFM_H__

typedef enum {
  BFM_VERSION       = 0x10001000,
  BFM_NOP           = 0x10001001,

  // Register Operations
  BFM_REG_RD_REQ    = 0x10002000,
  BFM_REG_RD_RESP   = 0x10002001,
  BFM_REG_WR_REQ    = 0x10002002,
  BFM_REG_WR_RESP   = 0x10002003,

  // Interrupts
  BFM_INT_SET       = 0x10003000,
  BFM_INT_CLR       = 0x10003001,
  BFM_INT_REQ_STAT  = 0x10003002,
  BFM_INT_STATUS    = 0x10003003,

  // Control
  BFM_END_SIM       = 0x10004000
} bfm_operations_t;

typedef enum {
  bfm_status_okay,
  bfm_status_error
} bfm_status_t;

typedef enum {
  socket_status_okay = 0,
  socket_status_fail = 1,
  socket_status_fail_create = 2,
  socket_status_bind_error = 3,
  socket_status_conn_fail = 4,
  socket_status_write_fail = 5,
  socket_status_client_dis = 6,
  socket_status_recv_fail = 7,
} socket_status_t;

// TODO: This needs to be 12 when it should only be 9, why???
#define BFM_INSTRUCTION_SIZE 20

typedef union {
  struct{
    bfm_operations_t    bfm_operation;
    uint8_t             bfm_len;
    uint32_t            bfm_parameter1;
    uint32_t            bfm_parameter2;
  };
  uint8_t           buf[BFM_INSTRUCTION_SIZE];
} bfm_instr_t;

#endif  //__BFM_H__

