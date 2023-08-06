#pragma once

namespace tx97
{
   enum Layer {
      TX_DZ = 0,
      TX_CL = 1,
      TX_DL = 2,
      TX_IB = 3,
      TX_LH = 4,
      TX_BO = 5,
      TX_RA = 6,
      TX_DP = 7,
      TX_DD = 8,
      TX_DG = 9,
      TX_LN = 10,
      TX_RT = 11,
      TX_CR = 12,
      TX_FL = 13,
      TX_TX = 14,
      TX_IN = 15,
      TX_OT = 16,
      TX_SB = 17,
      TX_HL = 18,
      TX_HG = 19,
      TX_HO = 20,
      LayersCount
   };

#pragma pack(1)

   // ����������� ��������� ����� ����� �� ����� 255 �������� (1 ����)
   struct TRS_STRING
   {
      unsigned char  N;       // ����� ������
      char           Data[1]; // ���������� ������
   }; // struct TRS_STRING

   // ����������� ��������� ����� ����� ����� 255 �������� (2 �����)
   struct TRS_LONGSTRING
   {
      unsigned short N;       // ����� ������
      char           Data[1]; // ���������� ������
   };

   // ��������� �������������� ��������� � ������� TX97
   struct TRS_GEO_POINT
   {
      short lat;  // ������
      short lon;  // �������
   }; // struct TRS_GEO_POINT

   //////////////////////////////////////////////////////////////////////////
   // ��������� ��������� ����� ������� TX97
   struct DESCRIPTION
   {
      char  Head[15];      // ��������� "TRANSAS CE v6.0"
      char  Date_corr[11]; // ���� ��������� ���������
      char  Chart_name[9]; // ��� �������� �����
      char  File_name[9];  // ��� ����������� �����
      float Delta_lat;     // �������� �� ������ ��� �������� � WGS
      float Delta_lon;     // �������� �� ������� ��� �������� � WGS
      float Latb;          // ���������� ����� ����� - ���������� �����a
      float Late;          // ���������� ����� ����� - ���������� �����a
      float Lonb;          // ���������� ����� ����� - ���������� �������
      float Lone;          // ���������� ����� ����� - ���������� �������
      float Latm;          // ������� ������
      float C0;            // ������� �������� �����
      short year_PD;       // ��� ������� �������� �����
      short month_PD;      // ����� ������� �������� �����
      short year_PP;       // ��� ������ �������� �����
      short month_PP;      // ����� ������ �������� �����
      short year_EC;       // ��� ������������ ����������� �����
      short month_EC;      // ����� ������������ ����������� �����
      char  Wgs;           // ���� ��� ��������� WGS ���������
      char  DP_mean;       // ������� ��������� �������
      char  LH_book;       // �������� ���������� �� �������� ������
      char  Datum;         // ���������
      char  Proj;          // ��������
      char  Type;          // ��� �����
      char  Cntr;          // ������ ������������ �������� �����
      char  LangP;         // ���� �������� �����
      char  LangE;         // ���� ����������� �����
      char  Reg;           // ������ ����/IALA
      char  CntG;          // ������/����������� �������� ����������
      char  compress;      // ��������������� ��� ��������� ���������� �����
      char  WaterLevel;    // ������� ����
      char  HO_mean;       // ������� ��������� ������
      char  TypeEx;        // ������ ����� (��. ���� Type)
      char  PubNum;        // ����� ������� �����
      char  CorrIssue;     // ����� ������� ��������� ��������� ����������
      char  Reserved[2];   // ��������������� (�� ������������)
      char  Revision;      // �������� ����� (������ ���� ����� 0)
   }; // struct DESCRIPTION

   struct DESCRIPTION_EX : DESCRIPTION
   {
      long Offsets[22]; // ������� ���������� �� ���� �����
   }; // struct DESCRIPTION_EX

   //////////////////////////////////////////////////////////////////////////
   // ��������� ������������
   struct TAIL
   {
      TRS_LONGSTRING name; // ������������ �����
   }; // struct TAIL

   //////////////////////////////////////////////////////////////////////////
   // \brief ��������� ������ ������
   struct CHARTLET
   {
      short          N;          // ���������� ����� � ������������� ���������
      TRS_GEO_POINT  points[1];  // ��������� �� ������ �� N ��������� ����� ���������
   }; // struct CHARTLET

   //////////////////////////////////////////////////////////////////////////
   // ��������� ������ ��������� �����
   struct COAST_LINE
   {
      short          N;          // ���������� ����� � ������������� ���������
      short          fs;         // �������� �����
      TRS_GEO_POINT  points[1];  // ��������� �� ������ �� N ��������� ����� ���������
   }; // struct COAST_LINE

   //////////////////////////////////////////////////////////////////////////
   // ��������� ������
   struct COVERS_AREA
   {
      short          N;          // �������������� ���������� ����������
      short          fs;         // �������� �����
      TRS_GEO_POINT  points[1];  // ��������� �� ������ �� N ��������� ����� ���������
   }; // struct COVERS_AREA

   //////////////////////////////////////////////////////////////////////////
   // \brief ��������� �������
   struct ISOBATHS
   {
      short          N;          // ���������� ����� � ������������� ���������
      unsigned short depth;      // �������� ������� � 1/10 ����� (� ����������)
      short          fs;         // �������� �����
      TRS_GEO_POINT  points[1];  // ��������� �� ������ �� N ��������� ����� ���������
   }; // struct ISOBATHS
   
   //////////////////////////////////////////////////////////////////////////
   ///��������� �����
   struct LIGHTHOUSE
   {
      TRS_GEO_POINT  point; // �������������� ���������� �����
      short          pe; // ������ ����
      char           ft; // �������������� ����
      char           nf; // ����� ����������/��������
      char           ra; ///<��������������, ������� p����� � ������
      char           ns; // ���������� ��������
      signed char    hl; // ������ �� ���������
      signed char    hs; // ������ �� ������ ����
      char           rn [  8 ]; // ������������ �����������
      char           un [ 10 ]; // ������������� �����������
      signed char    fl; // ����������� ����������� �����
      char           pr; // ��� �����
      char           tf; // ��� ������� ������ �����
      //����� ���� �������� ����� � TRS-������ (������������ ������������,
      //������������ ��������� �������, ��� � ���������)
   }; // struct LIGHTHOUSE

   // ��������� �������������� ���������� �������� � ������� ������
   struct LIGHTHOUSE_INFO
   {
      char  col;  // ����
      char  vl;   // ���������
      short ang;  // ��������� ���� (������� �������)
   }; // struct LIGHTHOUSE_INFO

   /// ���������, ����������� ������������ ���������� � ��������.
   struct FLASH_ECLIPSE
   {      
      char flash; ///< ��������.
      char eclipse; ///< ��������.
   }; // struct FLASH_ECLIPSE

   struct LIGHTHOUSE_DESC
   {
      const LIGHTHOUSE*       pLighthouse;
      const char*             pNfInfo;
      short                   nfInfoSize;
      const LIGHTHOUSE_INFO*  pLhInfo;
      short                   lhInfoNum;
      const TRS_STRING*       pName;
      const TRS_STRING*       pNote;
   };
   
   //////////////////////////////////////////////////////////////////////////
   // ��������� ���
   struct BUOY
   {
      TRS_GEO_POINT  point;   // �������������� ���������� ���
      short          pe;      // ������ ����
      char           ft;      // �������������� ����
      char           nf;      // ����� ����������/��������
      char           ra;      // ������� ������� ������
      char           tp;      // ��� ���
      char           bc;      // ���� ���������
      char           lc;      // ���� ����
      char           rn[8];   // ������������ �����������
      char           un[10];  // ������������� �����������
      // ����� ���� TRS-������ (��� � ���������)
   }; // struct BUOY

   struct BUOY_DESC
   {
      const BUOY*       pBuoy;
      const TRS_STRING* pName;
      const TRS_STRING* pNote;
   };

   //////////////////////////////////////////////////////////////////////////
   struct RACON
   {
      TRS_GEO_POINT  point;      // �������������� ���������� ������
      char           nm;         // ������� ���� ������
      char           morse[1];   // �������� ���� ����� � ������� ���������� �� ������� ������� � ����
   }; // struct RACON

   //////////////////////////////////////////////////////////////////////////
   // ��������� ������
   struct DEPTHS
   {
      TRS_GEO_POINT  point;   // �������������� ���������� �������
      unsigned short depth;   // �������
   }; // struct DEPTHS

   //////////////////////////////////////////////////////////////////////////
   // ��������� ������ �� �������
   struct COVERED_HEIGHTS
   {
      TRS_GEO_POINT  point;   //  �������������� ���������� ������ �� �������
      unsigned short depth;   // ������ �� ������
   }; // struct COVERED_HEIGHTS

   //////////////////////////////////////////////////////////////////////////
   // ��������� ������������� ���������
   struct ISOLATED_DANGER
   {
      TRS_GEO_POINT  point;   // �������������� ���������� ������������� ���������
      unsigned short depth;   // �������� ������ � 1/10 ����� ����� (����������)
      char           type;    // ��� ���������
      char           exist;   // ������� �������������
   }; // struct ISOLATED_DANGER

   //////////////////////////////////////////////////////////////////////////
   // ��������� ��������� �������
   struct LINE
   {
      short          N;          // ���������� ����� � ������������� ���������
      short          color;      // ���� �����
      short          style;      // ����� �����
      short          fill;       // ������� ��������� �����
      short          type;       // ��� �����
      TRS_GEO_POINT  points[1];  // ��������� �� ������ �� N ��������� ����� ���������
   }; // struct LINE

   //////////////////////////////////////////////////////////////////////////
   // ��������� ���������������� ��������
   struct RECOMMENDED_ROUTE
   {
      short          N;          // ���������� ����� � ������������� ���������
      unsigned short depth;      // �������� �������
      unsigned short dir1;       // �����������
      unsigned short type;       // ������� �����
      TRS_GEO_POINT  points[1];  // ��������� �� ������ �� N ��������� ����� ���������
   }; // struct RECOMMENDED_ROUTE

   //////////////////////////////////////////////////////////////////////////
   // ��������� ����������
   struct CIRCLE
   {
      TRS_GEO_POINT  point;   // �������������� ���������� ����������
      float          r;       // ������ � ������� �����
      short          sa;      // �� ������������
      short          ea;      // �� ������������
      short          kind;    // �� ������������
      short          color;   // ���� �����
      short          style;   // ����� �����
      short          fill;    // ������� ��������� �����
      short          type;    // ��� �����
   }; // struct CIRCLE

   //////////////////////////////////////////////////////////////////////////
   // ��������� �������
   struct STREAM
   {
      TRS_GEO_POINT  point;         // �������������� ���������� �������
      short          direction[13]; // ����������� ( � �������� )
      struct
      {
         char syzygy, quadrature;
      }              speed[13];     // �������� ( ������� � ���������� )
      short          num;           // ����� �������� ������
   }; // struct STREAM

   //////////////////////////////////////////////////////////////////////////
   // ��������� �������
   struct TEXT
   {
      TRS_GEO_POINT  point;   // �������������� ���������� �������
      short          color;   // ���� �������
      TRS_STRING     s;       // ��������� ������
   }; // struct TEXT

   //////////////////////////////////////////////////////////////////////////
   // ��������� ����������
   struct INFORMATION
   {
      TRS_GEO_POINT  point;   // �������������� ���������� ����������
      short          type;    // ��� ����������
      // ���������� ����� (�� ������������� ������������: �� ������������ ������ ���� 2 �����, � ������ - 1 ����)
      unsigned char  num;
      TRS_STRING     s[1];    // ������ ��������� �����
   }; // struct INFORMATION

   //////////////////////////////////////////////////////////////////////////
   ///���������, ����������� ������ �������
   struct OTHER_OBJECT
   {
      TRS_GEO_POINT  point;   // �������������� ���������� ������� �������
      short          type;    // ��� �������
   }; // struct OTHER_OBJECT

   //////////////////////////////////////////////////////////////////////////
   // ��������� ������
   struct SEABED_NATURE
   {
      TRS_GEO_POINT  point;   // �������������� ���������� ������
      TRS_STRING     s;       // ��������� ������
   }; // struct SEABED_NATURE

   //////////////////////////////////////////////////////////////////////////
   // ��������� �����������
   struct HORISONTAL_LANDMARKS
   {
      short          N;          // ���������� ����� � ������������� ���������
      unsigned short depth;      // �������� ������� / ������
      short          type;       // ��� �����
      TRS_GEO_POINT  points[1];  // ��������� �� ������ �� N ��������� ����� ���������
   }; // struct HORISONTAL_LANDMARKS

   //////////////////////////////////////////////////////////////////////////
   // ��������� ������������� ������
   struct HEIGHT
   {
      TRS_GEO_POINT  point;   // �������������� ���������� ������������� ������
      unsigned short depth;   // �������� ������ � ����������
      short          type;    // ��� �������
   }; // struct HEIGHT

   //////////////////////////////////////////////////////////////////////////
   // ��������� ���������� �������
   struct COASTAL_FEATURE
   {
      short          N;          // ���������� ����� � ������������� ���������
      short          color;      // ���� �����
      short          style;      // ����� �����
      short          fill;       // ������� ��������� �����
      short          type;       // ��� �����
      TRS_GEO_POINT  points[1];  // ������ �� N ��������� ����� ���������
   }; // struct COASTAL_FEATURE

#pragma pack()

   //////////////////////////////////////////////////////////////////////////

   // ������������ ����� ���� ������, �� �������� ��������� ������������
   inline long calc_check_sum ( const void* pData, unsigned szData )
   {
      const unsigned char* pBytes = reinterpret_cast<const unsigned char*>( pData );

      long crc = 0;
      for ( unsigned i = 0; i < szData; ++i )
         crc += pBytes[ i ];

      return crc;
   }

}