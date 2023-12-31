//**********************************************************************//
// File:        systemInit.c                                            //
// Description: Source file that contains the functions and methods     //
//              implementations for system initializing task            //
// Author:      Leonardo Rossi Leao                                     //
// Reviewer:    Rodrigo Moreira Bacurau                                 //
// Last Update: 2023-11-13                                              //
//**********************************************************************//

#include "systemInit.h"

extern Axis xAxes;
extern osThreadId_t systemControlHandle;
extern lcdSettings_t xLcdSettings;
extern sensorReadings_t xSensorReadings;

uint8_t cTeste;

//**********************************************************************//
// Method:      vSystemInitStart                                        //
// Description: Entrypoint to line follower robot initializing task     //
// Input:       none                                                    //
// Output:      none                                                    //
//**********************************************************************//
void vSystemInitStart()
{
	vLcdInit();
	vSensorReadingsInit();
	vCommunicationInit(&huart3, &huart7);

	HAL_UART_Receive_IT(&huart6, &cTeste, 1);
	HAL_TIM_Base_Start_IT(&htim7);

	osThreadFlagsSet(systemControlHandle, 0b1);

	vActuatorConfigSin(0.1, 8*3.14/181, 0, 0);

	lcdMessage_t xOdometryMessage1 = {
		.uiTime               = 1000,
		.cFirstLine           = "Lat: %.2f",
		.pFirstLineValue      = &xSensorReadings.xGPS.fLatitude,
		.cSecondLine          = "Lon: %.2f",
		.pSecondLineValue     = &xSensorReadings.xGPS.fLongitude,
		.uiFirstLineHasValue  = LCD_YES,
		.uiSecondLineHasValue = LCD_YES,
	};
	vLcdAppendMessageToCarrousel(xOdometryMessage1);

	lcdMessage_t xOdometryMessage2 = {
		.uiTime               = 1000,
		.cFirstLine           = "Acc-X: %.4f",
		.pFirstLineValue      = &xSensorReadings.xIMU.xAccelerometer.fX,
		.cSecondLine          = "Acc-Z: %.4f",
		.pSecondLineValue     = &xSensorReadings.xIMU.xAccelerometer.fZ,
		.uiFirstLineHasValue  = LCD_YES,
		.uiSecondLineHasValue = LCD_YES,
	};
	vLcdAppendMessageToCarrousel(xOdometryMessage2);

	lcdMessage_t xOdometryMessage3 = {
		.uiTime               = 1000,
		.cFirstLine           = "Temp: %.2f",
		.pFirstLineValue      = &xSensorReadings.xIMU.fTemperature,
		.cSecondLine          = "",
		.uiFirstLineHasValue  = LCD_YES,
		.uiSecondLineHasValue = LCD_NO,
	};
	vLcdAppendMessageToCarrousel(xOdometryMessage3);



	while(1)
	{
		osDelay(1000);
	}
}

//**********************************************************************//
// Method:      HAL_UART_RxCpltCallback                                 //
// Description: UART interruption callback                              //
// Parameters:  UART_HandleTypdef *: UART that trigger the interruption //
// Returns:     n/a                                                     //
//**********************************************************************//
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
	// UART communication wired and bluetooth
	if(huart == &huart3 || huart == &huart7)
		vCommunicationLPUART1Callback();
	if(huart == &huart6)
		vGPSUartCallback();
}


void HAL_FDCAN_RxFifo0Callback(FDCAN_HandleTypeDef *hfdcan, uint32_t RxFifo0ITs)
{
	if((RxFifo0ITs & FDCAN_IT_RX_FIFO0_NEW_MESSAGE) != RESET)
	{
		FDCAN_RxHeaderTypeDef RxHeader;
		uint8_t RxData[8];

		// Retrieve RX messages from RX FIFO0
		if (HAL_FDCAN_GetRxMessage(hfdcan, FDCAN_RX_FIFO0, &RxHeader, RxData) != HAL_OK)
			Error_Handler();
		else
			ODrive_RX_CallBack(&xAxes, &RxHeader, RxData);
	}
}
