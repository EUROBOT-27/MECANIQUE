
#include "NavStateMachineTest.h"
#include "NavConfig.h"
#include "NavTypes.h"
#include "NavConstants.h"
#include "Navigation.h"
#include "math.h"

#define NAV_SA_INIT_X_MM        0.0
#define NAV_SA_INIT_Y_MM        0.0
#define NAV_SA_INIT_ANGLE_DEG   0.0

typedef struct {
    double  targetX_mm;
    double  targetY_mm;
    double  arrivingAngle_deg;
    uint8_t direction;
    double  linearVelocity;
    double  angularVelocity;
    double  linearAcc;
    double  angularAcc;
    uint8_t withPlatforms;
} Nav_SA_Waypoint_t;

static const Nav_SA_Waypoint_t Nav_Waypoints[] =
{
    /*  X       Y      finalAngle  dir                    Vlin  Vang  Alin  Aang  platforms               */
		{  1000, 0,0, ROBOT_Going_Forward,  650,  180,  900,  200,  ROBOT_Without_Platforms },
	/*{  533.2, 1200, 180, ROBOT_Going_Forward,  650,  180,  1200,  200,  ROBOT_Without_Platforms },
    {  400, 1200, 180,  ROBOT_Going_Forward,  650,  180,  1200,  200,  ROBOT_Without_Platforms },
    {  950, 660, 135,  ROBOT_Going_Backward,  650,  180,  1200,  200,  ROBOT_Without_Platforms },
    {  1100, 550, 270,  ROBOT_Going_Backward,  650,  180,  1200,  200,  ROBOT_Without_Platforms },
    {  1100, 420, 270, ROBOT_Going_Forward,  650,  180,  1200,  200,  ROBOT_Without_Platforms },
    {  1250, 225, 0,  ROBOT_Going_Forward,  650,  180,  1200,  200,  ROBOT_Without_Platforms },
	{  770, 225, 0,  ROBOT_Going_Backward,  650,  180,  1200,  200,  ROBOT_Without_Platforms },
    {  738, 420, 270, ROBOT_Going_Backward,  650,  180,  1200,  200,  ROBOT_Without_Platforms },
    {  420, 400, 180,  ROBOT_Going_Forward,  650,  180,  1200,  200,  ROBOT_Without_Platforms },

	{  300, 1550, 90,  ROBOT_Going_Forward,  650,  180,  1200,  200,  ROBOT_Without_Platforms },
	{  300, 1687, 90,ROBOT_Going_Forward,  650,  180,  1200,  200,  ROBOT_Without_Platforms },*/


   // {  200.0,  100,   0,  ROBOT_Going_Forward,  650,  180,  1200,  200,  ROBOT_Without_Platforms },

};

#define NAV_SA_WAYPOINT_COUNT  ( sizeof(Nav_Waypoints) / sizeof(Nav_SA_Waypoint_t) )


volatile uint8_t Nav_SA_StopRequested  = 0;
volatile uint8_t Nav_SA_ResetRequested = 0;


static uint8_t Nav_SA_CurrentWaypointIndex = 0;
static uint8_t Nav_SA_Initialised          = 0;

static uint8_t Nav_SA_Finished = 0;


extern double  Nav_TargetX_mm_d;
extern double  Nav_TargetY_mm_d;
extern double  Nav_TargetArrivingAngle_deg_d;
extern double  Nav_CurrentX_mm_d;
extern double  Nav_CurrentY_mm_d;
extern double  Nav_CurrentAngle_deg_d;
extern double  Nav_CurrentAngle_rad_d;
extern double  Nav_CurrentTargetAngle_deg_d;
extern double  Nav_PrevTargetAngle_deg_d;
extern double  Nav_vitessemax;
extern double  Nav_MaxAngularVitesse;
extern double  Nav_Accel;
extern double  Nav_AngularAccel;

extern uint8_t ROBOT_Direction;
extern uint8_t Nav_withPlatforms;

extern Nav_NavigatorCurrentStates_ten Nav_NavigatorCurrentState_en;
extern Nav_GoToXY_States_ten          Nav_GoToXY_State_en;
extern Nav_TrajectoryModes_ten        Nav_TrajectoryMode_en;
extern Nav_TrapezePhases_ten          Nav_TrapezePhase_en;

extern int32_t MINIMUM_RIGHT_MOTOR_FORWARD_COMMAND;
extern int32_t MINIMUM_RIGHT_MOTOR_REVERSE_COMMAND;
extern int32_t MINIMUM_LEFT_MOTOR_FORWARD_COMMAND;
extern int32_t MINIMUM_LEFT_MOTOR_REVERSE_COMMAND;
extern double  MINIMUM_SATURATION_COMMAND;



static void Nav_SA_LoadWaypoint(uint8_t index)
{
    const Nav_SA_Waypoint_t *wp = &Nav_Waypoints[index];
    Nav_TargetX_mm_d              = wp->targetX_mm;
    Nav_TargetY_mm_d              = wp->targetY_mm;
    Nav_TargetArrivingAngle_deg_d = wp->arrivingAngle_deg;
    ROBOT_Direction               = wp->direction;
    Nav_vitessemax                = wp->linearVelocity;
    Nav_MaxAngularVitesse         = wp->angularVelocity;
    Nav_Accel                     = wp->linearAcc;
    Nav_AngularAccel              = wp->angularAcc;
    Nav_withPlatforms             = wp->withPlatforms;
}

static void Nav_SA_ApplyMinimumCommands(uint8_t withPlatforms)
{
    if (withPlatforms == ROBOT_With_Platforms) {
        MINIMUM_COMMANDS_WITH_PLATFORMS
    } else {
        MINIMUM_COMMANDS_WITHOUT_PLATFORMS
    }
}



void Nav_vStandaloneStateMachine_Routine(void)
{
    if (Nav_SA_ResetRequested) {
        Nav_SA_ResetRequested = 0;
        SCB->AIRCR = 0x05FA0004;
    }

    if (Nav_SA_StopRequested) {
        Nav_SA_StopRequested = 0;
        Nav_NavigatorCurrentState_en = MASTER_NavigatorOrderSuddenStop_en;
    }

    switch (Nav_NavigatorCurrentState_en)
    {


    case MASTER_NavigatorIdle_en:
    {
        if (Nav_SA_Finished) {
            break;
        }

        if (!Nav_SA_Initialised) {
            Nav_SA_Initialised           = 1;
            Nav_SA_CurrentWaypointIndex  = 0;

            Nav_CurrentX_mm_d            = 0;
            Nav_CurrentY_mm_d            = 0;
            Nav_CurrentAngle_deg_d       = 0;
            Nav_CurrentAngle_rad_d       = (3.1415 / 180.0) *0;
            Nav_CurrentTargetAngle_deg_d = 0;
            Nav_PrevTargetAngle_deg_d    = 0;
        }

        Nav_NavigatorCurrentState_en = MASTER_NavigatorReady_en;
    }
    break;

    case MASTER_NavigatorInit_en:
    {
        Nav_NavigatorCurrentState_en = MASTER_NavigatorReady_en;
    }
    break;

    case MASTER_NavigatorReady_en:
    {
        if (Nav_SA_CurrentWaypointIndex < NAV_SA_WAYPOINT_COUNT) {
            Nav_SA_LoadWaypoint(Nav_SA_CurrentWaypointIndex);
            Nav_SA_ApplyMinimumCommands(Nav_Waypoints[Nav_SA_CurrentWaypointIndex].withPlatforms);
            Nav_SA_CurrentWaypointIndex++;
            Nav_NavigatorCurrentState_en = MASTER_NavigatorBusy_en;
        } else {

            Nav_SA_Finished = 1;
            Nav_NavigatorCurrentState_en = MASTER_NavigatorIdle_en;
        }
    }
    break;

    case MASTER_NavigatorBusy_en:
    {
        Nav_vDetectBlockage();

        Nav_navigationSimulation(
            &Nav_TargetX_mm_d,
            &Nav_TargetY_mm_d,
            &Nav_TargetArrivingAngle_deg_d,
            &ROBOT_Direction,
            &Nav_withPlatforms
        );

        if (Nav_GoToXY_State_en == Nav_GoToXY_Idle_en) {
            Nav_NavigatorCurrentState_en = MASTER_NavigatorReachedDest_en;
        }
    }
    break;

    case MASTER_NavigatorReachedDest_en:
    {
        Nav_NavigatorCurrentState_en = MASTER_NavigatorReady_en;
    }
    break;

    case MASTER_NavigatorOrderSuddenStop_en:
    {
        Nav_NavigatorCurrentState_en = MASTER_NavigatorSuddenStop_en;

        if (   Nav_GoToXY_State_en == Nav_GoToXY_Rotate_en
            || Nav_GoToXY_State_en == Nav_GoToXY_Forward_en
            || Nav_GoToXY_State_en == Nav_GoToXY_RotateAfter_en)
        {
            Nav_GoToXY_State_en = Nav_GoToXY_OrderSuddenStop_en;
        }
    }
    break;

    case MASTER_NavigatorSuddenStop_en:
    {
        if (Nav_GoToXY_State_en == Nav_GoToXY_Idle_en) {
            Nav_NavigatorCurrentState_en = MASTER_NavigatorConfirmedStop_en;
        } else {
            Nav_navigationSimulation(
                &Nav_TargetX_mm_d,
                &Nav_TargetY_mm_d,
                &Nav_TargetArrivingAngle_deg_d,
                &ROBOT_Direction,
                &Nav_withPlatforms
            );
        }
    }
    break;

    case MASTER_NavigatorConfirmedStop_en:
    {
    }
    break;

    case MASTER_NavigatorBlockageDetected_en:
    {
        Nav_navigationSimulation(
            &Nav_TargetX_mm_d,
            &Nav_TargetY_mm_d,
            &Nav_TargetArrivingAngle_deg_d,
            &ROBOT_Direction,
            &Nav_withPlatforms
        );
        Nav_NavigatorCurrentState_en = MASTER_NavigatorReady_en;
    }
    break;

    case MASTER_NavigatorWallBlockageDetected_en:
    {
        Nav_navigationSimulation(
            &Nav_TargetX_mm_d,
            &Nav_TargetY_mm_d,
            &Nav_TargetArrivingAngle_deg_d,
            &ROBOT_Direction,
            &Nav_withPlatforms
        );
        Nav_NavigatorCurrentState_en = MASTER_NavigatorReady_en;
    }
    break;

    default:
        break;
    }
}
