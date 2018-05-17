/////////////////////////////////////////////////////////////////////////////
//
//                                    Server
//
/////////////////////////////////////////////////////////////////////////////

#include <stdio.h>
#include <string.h>    //strlen
#include <sys/socket.h>
#include <arpa/inet.h> //inet_addr
#include <unistd.h>    //write

#include "bfm.h"

// The one and only sock that we talk to
int client_sock;


// Testbench SV exported functions
extern int svDelay(int *t);
extern int tb_read_request(int rd_addr,int *rd_data,int *rd_status);

void dump_packet(bfm_instr_t pck)
{
  int i = 0;
  for(i=0;i<BFM_INSTRUCTION_SIZE;i++)
    printf("%2.0d-0x%X\t", i, pck.buf[i]);
  printf("\n");
}


int open_connection(int *status)
{
    int socket_desc,c;
    struct sockaddr_in server, client;

    //Create socket
    socket_desc = socket(AF_INET , SOCK_STREAM , 0);
    if (socket_desc == -1)
    {
        printf("[server] Could not create socket");
        *status  = socket_status_fail_create;
        return socket_status_fail;
    }
    puts("[server] Socket created");
     
    //Prepare the sockaddr_in structure
    server.sin_family = AF_INET;
    server.sin_addr.s_addr = INADDR_ANY;
    server.sin_port = htons( 8888 );
     
    //Bind
    if( bind(socket_desc,(struct sockaddr *)&server , sizeof(server)) < 0)
    {
        //print the error message
        perror("[server] Bind failed. Error");
        *status = socket_status_bind_error;
        return socket_status_fail;
    }
    puts("[server] Bind done");
     
    //Listen
    listen(socket_desc , 3);
     
    //Accept and incoming connection
    puts("[server] Waiting for incoming connections...");
    c = sizeof(struct sockaddr_in);
     
    //accept connection from an incoming client
    client_sock = accept(socket_desc, (struct sockaddr *)&client, (socklen_t*)&c);
    if (client_sock < 0)
    {
        perror("[server] Accept failed");
        *status = socket_status_conn_fail;
        return socket_status_fail;
    }

    puts("[server] Connection accepted");
  
  return socket_status_okay;
}

void send_resp(bfm_instr_t resp)
{

    if( send(client_sock, resp.buf, BFM_INSTRUCTION_SIZE, 0) < 0)
    {
        puts("[server] Send read request failed\n");
    }

}

void read_request(uint32_t rd_addr)
{
  uint32_t rd_data;
  uint32_t rd_status;

  // TODO: check status
  tb_read_request(rd_addr, &rd_data, &rd_status);
  printf("[server] Read 0x%X from 0x%X\n", rd_data, rd_addr);
  read_response(rd_data);
}

void read_response(uint32_t rd_data)
{
  bfm_instr_t resp;

  resp.bfm_operation = BFM_REG_RD_RESP;
  resp.bfm_len = BFM_INSTRUCTION_SIZE;
  resp.bfm_parameter1 = rd_data;

  send_resp(resp);
}

void write_request(uint32_t wr_addr, uint32_t wr_data)
{
  uint32_t wr_status;

  printf("[server] Got write request of 0x%X on address 0x%X\n", wr_data, wr_addr);
  tb_write_request(wr_addr, wr_data, &wr_status);

  // TODO: check status
  write_response(bfm_status_okay);
}

void write_response(bfm_status_t status)
{
  bfm_instr_t resp;

  // Now let the client know how the write went
  resp.bfm_operation = BFM_REG_WR_RESP;
  resp.bfm_len = BFM_INSTRUCTION_SIZE;
  resp.bfm_parameter1 = status;

  send_resp(resp);
}

bfm_operations_t decode_client_request(bfm_instr_t hdr)
{
  
  printf("[server] Decoding operation 0x%X\n", hdr.bfm_operation);

  //dump_packet(hdr);

  switch(hdr.bfm_operation) {
    case BFM_VERSION:
    case BFM_NOP:
    case BFM_REG_RD_REQ:  
      read_request(hdr.bfm_parameter1); 
      break;
    case BFM_REG_WR_REQ:
      write_request(hdr.bfm_parameter1,hdr.bfm_parameter2);
      break;
    case BFM_INT_SET:
    case BFM_INT_CLR:
    case BFM_INT_STATUS:
      write_response(bfm_status_okay);
      break;
    case BFM_END_SIM:      
      printf("[server] End Simulation\n"); 
      break;
    default:
      printf("[server] Unexpected request 0x%X\n", hdr.bfm_operation);
  };

  return(hdr.bfm_operation);
}

bfm_operations_t parse_client_request()
{
    bfm_instr_t hdr;
    char  client_message[255];
    int   recv_resp;

    //Receive a message from client
    recv_resp = recv(client_sock, client_message, 255, 0);

    if(recv_resp == 0)
    {
        puts("[server] Client disconnected");
        fflush(stdout);
        return BFM_END_SIM;
    }
    else if(recv_resp == -1)
    {
        perror("[server] recv failed");
        return BFM_END_SIM;
    }

    memcpy(hdr.buf, client_message, BFM_INSTRUCTION_SIZE);

    return decode_client_request(hdr);
}

// This is the function that is exported for use with SV
// Just a wrapper around the actual parser
int export_parse_client_request(int *request){
  bfm_operations_t op;
  op = parse_client_request();
  *request = (int*)op;
  return 0;
}

#ifdef CPP_PROG
int main(int argc , char *argv[])
{
    bfm_operations_t  recv_resp = BFM_NOP;
    socket_status_t   status;

    if(open_connection((int*)&status) != 0)
      return -1;

    while(recv_resp != BFM_END_SIM) 
      recv_resp = parse_client_request();

    fflush(stdout);
    return 0;
}
#endif
