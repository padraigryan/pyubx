/////////////////////////////////////////////////////////////////////////////
//
//                                   Client 
//
/////////////////////////////////////////////////////////////////////////////
//
#include <stdio.h> //printf
#include <string.h>    //strlen
#include <sys/socket.h>    //socket
#include <arpa/inet.h> //inet_addr
#include <unistd.h>    //write

#include "bfm.h"
 
int sock = -1;

uint32_t open_connection()
{
    struct sockaddr_in server;
    char message[1000] , server_reply[2000];
    bfm_instr_t hdr;
    int recv_resp;

    //Create socket
    sock = socket(AF_INET , SOCK_STREAM , 0);
    if (sock == -1)
    {
        printf("[client] Could not create socket");
        return -1;
    }
    //puts("[client] Socket created");
     
    server.sin_addr.s_addr = inet_addr("127.0.0.1");
   // server.sin_addr.s_addr = inet_addr("172.29.227.71");
    server.sin_family = AF_INET;
    server.sin_port = htons( 8888 );
 
    //Connect to remote server
    while (connect(sock , (struct sockaddr *)&server , sizeof(server)) < 0)
    {
        perror("[client] connect failed. Error");
        return -1;
    }
     
    //puts("[client] Connected\n");
    return 0;
}


uint32_t send_request(bfm_instr_t req)
{
    if( send(sock, req.buf, BFM_INSTRUCTION_SIZE, 0) < 0)
    {
        puts("[client] Send request failed");
        return BFM_END_SIM;
    }
}

socket_status_t get_response(uint32_t *resp)
{
    bfm_instr_t req;
    int32_t recv_resp;

    recv_resp = recv(sock, req.buf, BFM_INSTRUCTION_SIZE, 0);

    if(recv_resp == 0)
    {
        puts("[client] Client disconnected");
        *resp = BFM_END_SIM;
        return socket_status_client_dis;
    }
    else if(recv_resp == -1)
    {
        perror("[client] recv failed");
        *resp = BFM_END_SIM;
        return socket_status_recv_fail;
    }

    *resp = req.bfm_parameter1;
    return socket_status_okay;
}

uint32_t reg_write(uint32_t addr, uint32_t data)
{
    bfm_instr_t   wr_req;
    uint32_t   wr_resp;
    if(sock == -1)
      open_connection();

    //printf("[client] Sending Write of 0x%X Request to 0x%X\n", data, addr);

    wr_req.bfm_operation = BFM_REG_WR_REQ;
    wr_req.bfm_len = BFM_INSTRUCTION_SIZE;
    wr_req.bfm_parameter1 = addr;
    wr_req.bfm_parameter2 = data;

    // Send the write request
    send_request(wr_req);

    //Receive data back from server
    if(get_response(&wr_resp) == socket_status_okay) {
        //printf("[client] Write okay\n");
    } else {
        printf("[client] Write failed\n");
        return socket_status_write_fail;
    }

    return socket_status_okay;
}

uint32_t reg_read(unsigned int addr)
{
    bfm_instr_t rd_req;
    unsigned int rd_data;

    if(sock == -1)
      open_connection();
  
    //printf("[client] Sending Read Request to 0x%X\n", addr);

    rd_req.bfm_operation = BFM_REG_RD_REQ;
    rd_req.bfm_len = BFM_INSTRUCTION_SIZE;
    rd_req.bfm_parameter1 = addr;

    // Send the read request
    send_request(rd_req);

    get_response(&rd_data);
    
    //printf("[client] Read 0x%X from 0x%X\n", rd_data, addr);
    return rd_data;
}

uint32_t end_sim()
{
    bfm_instr_t end_req;
    if(sock == -1)
      open_connection();

    //printf("[client] Sending end of sim request\n");
    end_req.bfm_operation = BFM_END_SIM;
    end_req.bfm_len       = BFM_INSTRUCTION_SIZE;

    //Send some data
    if( send(sock, end_req.buf, BFM_INSTRUCTION_SIZE, 0) < 0)
    {
        puts("[client] Send end of sim request failed");
        return 1;
    }

}

uint32_t check_for_interrupt()
{
    bfm_instr_t   int_st_req;
    uint32_t      int_status;

    if(sock == -1)
      open_connection();
  
    int_st_req.bfm_operation = BFM_INT_STATUS;
    int_st_req.bfm_len       = BFM_INSTRUCTION_SIZE;

    // Send the read request
    send_request(int_st_req);

    if(get_response(&int_status) != socket_status_okay)
      printf("[client] Interupt status check failed \n");

    //printf("[client] Interupt status is 0x%X\n", int_status);
    return int_status;
}

#ifdef CPP_PROG
int main(int argc , char *argv[])
{
    if(open_connection() < 0)
      return -1;

    // Check for interupt
    check_for_interrupt();
/*    reg_read(64);
    reg_write(64, 0xDEADBEEF);
    reg_read(64);
    end_sim();
  */   
    close(sock);
    fflush(stdout);
    return 0;
}

#endif
