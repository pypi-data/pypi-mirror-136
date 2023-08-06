/*
 *
 */

#ifndef  SOFTCORR_H
#define  SOFTCORR_H

#define  DasHeaderKey   1031
#define  DasBufferKey   1032

#include  <sys/ipc.h>
#include  <sys/shm.h>
#include  <sys/types.h>

#define  BeamBufferSize  (64*1024*1024)/(4)
#define  IABeamBufferSize  (64*1024*1024)/(4)
#define  MaxDataBlocks  8
#define  TimeSize       sizeof(double)

enum BufFlag { _BufMarked=1, _BufReady=1<<1, _BufOverflow=1<< 2, _BufFinish=1<<3, _MaxBufs=100 };

typedef struct
{
  unsigned int flag, curBlock, curRecord, blockSize;
  int overFlow;
  double pcTime[MaxDataBlocks],dataTime[MaxDataBlocks];
  char data[BeamBufferSize*MaxDataBlocks];
} DataBuffer;

typedef struct
{
  unsigned int flag, curBlock, curRecord, blockSize;
  int overFlow;
  double pcTime[MaxDataBlocks],dataTime[MaxDataBlocks];
  short int data[IABeamBufferSize*MaxDataBlocks];
} DataBufferIA;

typedef struct
{
  unsigned int active, status;
  char file[100];
  double pcTime, dataTime, refTime;
  struct timeval timestamp;
} DataHeader;

#endif  // SOFTCORR_H
