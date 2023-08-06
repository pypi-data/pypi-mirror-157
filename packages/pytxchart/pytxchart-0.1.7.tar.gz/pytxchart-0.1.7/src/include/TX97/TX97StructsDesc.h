#pragma once

namespace tx97 {

// ���� ��������
namespace projection {
   int const Mercator            = 0; // Mercator
   int const TransverseMercator  = 1; // Transverse Mercator
   int const Gnomonic            = 2; // Gnomonic
   int const Polyconic           = 3; // Polyconic
   int const Gauss               = 4; // Gauss
   int const UTM                 = 5; // UTM
}


// ���� ���������
namespace ellipsoid {
   int const Krassovsky          = 0;  // Krassovsky
   int const Airy                = 1;  // Airy
   int const ModAiry             = 2;  // Mod. Airy
   int const AustralNation       = 3;  // Austral. Nation.
   int const Bessel_1841         = 4;  // Bessel 1841
   int const BesselNamibia_1841  = 5;  // Bessel 1841(Namibia)
   int const Clarke_1866         = 6;  // Clarke 1866
   int const Clarke_1880         = 7;  // Clarke 1880
   int const EverestBrunei       = 8;  // Everest(Brunei)
   int const EverestIndia_1830   = 9;  // Everest(India 1830)
   int const EverestIndia_1956   = 10; // Everest(India 1956)
   int const EverestMalasia_1948 = 11; // Everest(W Malasia 1948)
   int const EverestMalasia_1969 = 12; // Everest(W Malasia 1969)
   int const ModEverest          = 13; // Mod.Everest
   int const Fischer_1960        = 14; // Fischer 1960 /Mercury/
   int const ModFischer_1960     = 15; // Mod. Fischer 1960
   int const Fischer_1968        = 16; // Fischer 1968
   int const GRS_1967            = 17; // GRS 1967
   int const GRS_1980            = 18; // GRS 1980
   int const Helmert_1906        = 19; // Helmert 1906
   int const Hough               = 20; // Hough
   int const International       = 21; // International
   int const SouthAmerican_1969  = 22; // South American 1969
   int const WGS_60              = 23; // WGS 60
   int const WGS_66              = 24; // WGS 66
   int const WGS_72              = 25; // WGS 72
   int const WGS_84              = 26; // WGS 84
   int const Unknown             = 27; // Unknown
   int const Everest             = 28; // Everest
}


// ������� ��������� ������/�����.
namespace depth_height_unit {
   int const Metre      = 0;  // �����
   int const Foot       = 1;  // ����
   int const FootSazhen = 2;  // ����+������
   int const Sazhen     = 3;  // ������
}


// ������-������������ �������� �����
namespace chart_provider {
   int const Russia_P               = 0;  // ������
   int const England_P              = 1;  // ������
   int const USA_P                  = 2;  // USA
   int const France_P               = 3;  // �������
   int const Norway_P               = 4;  // ��������
   int const Sweden_P               = 5;  // ������
   int const Finland_P              = 6;  // ���������
   int const Germany_P              = 7;  // ��������
   int const Australia_P            = 8;  // ���������
   int const NewZealand_P           = 9;  // �.��������
   int const IntOrganisations_P     = 10; // ������������� �����������
   int const Denmark_P              = 11; // �����
   int const Holland_P              = 12; // ���������
   int const SouthKorea_P           = 13; // �.�����
   int const Spain_P                = 14; // �������
   int const Canada_P               = 15; // ������
   int const SouthAfricanRepublic_P = 16; // ���
   int const India_P                = 17; // �����
   int const Brazil_P               = 18; // ��������
   int const Surinam_P              = 19; // �������
   int const Poland_P               = 20; // ������
   int const Argentina_P            = 21; // ���������
   int const Ecuador_P              = 22; // �������
   int const Italy_P                = 23; // ������
   int const Latvia_P               = 24; // ������
   int const Estonia_P              = 25; // �������
   int const Chile_P                = 26; // ����
   int const Iceland_P              = 27; // ��������
   int const Indonesia_P            = 28; // ���������
   int const Croatia_P              = 29; // ��������
}


// ������/�����������-�������� ����������
namespace information_owner {
   int const NotDefined_I           = 0;  // �� ����������
   int const Russia_I               = 1;  // ������
   int const England_I              = 2;  // ������
   int const USA_I                  = 3;  // USA
   int const France_I               = 4;  // �������
   int const Norway_I               = 5;  // ��������
   int const Sweden_I               = 6;  // ������
   int const Finland_I              = 7;  // ���������
   int const Germany_I              = 8;  // ��������
   int const Australia_I            = 9;  // ���������
   int const NewZealand_I           = 10; // �.��������
   int const Denmark_I              = 11; // �����
   int const Holland_I              = 12; // ���������
   int const SouthKorea_I           = 13; // �.�����
   int const Spain_I                = 14; // �������
   int const Canada_I               = 15; // ������
   int const SouthAfricanRepublic_I = 16; // ���
   int const India_I                = 17; // �����
   int const Brazil_I               = 18; // ��������
   int const Surinam_I              = 19; // �������
   int const Poland_I               = 20; // ������
   int const Argentina_I            = 21; // ���������
   int const Ecuador_I              = 22; // �������
   int const Italy_I                = 23; // ������
   int const Latvia_I               = 24; // ������
   int const Estonia_I              = 25; // �������
   int const Chile_I                = 26; // ����
   int const Iceland_I              = 27; // ��������
   int const Indonesia_I            = 28; // ���������
   int const Croatia_I              = 29; // ��������
}


// ������ ����/IALA
namespace region {
   int const A = 0;
   int const B = 1;
}


// ������� ����
namespace water_level_type {
   int const Full      = 0;   // ������
   int const Few       = 1;   // �����
   int const UnDefined = 2;   // �� ����������
}


// �������� ���������� �� ��������  ������
namespace information_sourse {
   int const RussianBook  = 0; // �� ������� ������
   int const EnglishBook  = 1; // �� ���������� ������
   int const AmericanBook = 2; // �� ������������ ������
}


// ���� ��������/����������� �����
namespace language {
   int const Russian    = 0;  // �������
   int const English    = 1;  // ����������
   int const French     = 2;  // �����������
   int const Norwegian  = 3;  // ����������
   int const Swedish    = 4;  // ��������
   int const Finnish    = 5;  // �������
   int const German     = 6;  // ��������
   int const Dutch      = 7;  // �����������
   int const Danish     = 8;  // �������
   int const Portuguese = 9;  // �������������
   int const Polish     = 10; // ��������
   int const Spanish    = 11; // ���������
   int const Italian    = 12; // �����������
}

// �������� ����� �������
namespace isobaths_fs {
   int const FillRT     = 0x0001;  // ����������� ������ ��� ����� ����� ������ ������� �������
   int const RESERVED   = 0x0002;  // �� ����������
   int const AR_CO      = 0x0004;  // ������� ������ ������
   int const FillOut    = 0x0008;  // ������� ������� �������
   int const BreakLine  = 0x0010;  // ����� �� ��������
}

//////////////////////////////////////////////////////////////////////////
// ��� ���� �����
namespace lighthouse_ft {
   int const Unknown                         = 0;  // �����������
   int const Fixed                           = 1;  // ����������
   int const Isophase                        = 2;  // ���������
   int const Flashing                        = 3;  // ������������
   int const GroupFlashing                   = 4;  // ��. ������������
   int const CompositeGroupFlashing          = 5;  // ��. ��. ������������
   int const Occulting                       = 6;  // �������������
   int const GroupOcculting                  = 7;  // ��.�������������
   int const CompositeGroupOcculting         = 8;  // ��. ��. �������������
   int const LongFlashing                    = 9;  // ��.������������
   int const GroupLongFlashing               = 10; // ��. ��. ������������
   int const MorseCode                       = 11; // �� ������ �����
   int const Quick                           = 12; // ������
   int const GroupQuick                      = 13; // ��. ������
   int const GroupQuickAndLongFlashing       = 14; // ��. ������ � ��. �����.
   int const InterruptedQuick                = 15; // ����. ������
   int const VeryQuick                       = 16; // ����� ������
   int const GroupVeryQuick                  = 17; // ��. ����� ������
   int const GroupVeryQuickAndLongFlashing   = 18; // ��. ��. ������ � ��. �����.
   int const InterruptedVeryQuick            = 19; // ����. ����� ������
   int const UltraQuick                      = 20; // ������������
   int const InterruptedUltraQuick           = 21; // ����. ������������
   int const FixedOcculting                  = 22; // ���������� � ����.
   int const FixedAndGroupOcculting          = 23; // ���������� � ��. ����.
   int const FixedIsophase                   = 24; // ���������� � ���������
   int const FixedFlashing                   = 25; // ���������� � �����.
   int const FixedAndGroupFlashing           = 26; // ���������� � ��. �����.
   int const FixedLongflashing               = 27; // ���������� � ��. �����.
   int const Alternating                     = 28; // ����������
   int const AlternatingOcculting            = 29; // ���������� ����.
   int const AlternatingFlashing             = 30; // ���������� �����.
   int const AlternatingGroupFlashing        = 31; // ���������� ��. �����.
}

// ����, ��� ������� �� ���������� nf_info
const int NoNfInfoTypes[] = {
   lighthouse_ft::Unknown,  // �� ��������� � ������������� (�� Sahara)
   lighthouse_ft::Fixed, 
   lighthouse_ft::Isophase, 
   lighthouse_ft::Quick, 
   lighthouse_ft::VeryQuick,
   lighthouse_ft::UltraQuick
};

inline bool is_nf_info_type ( int ft )
{
   return ( std::find(NoNfInfoTypes, NoNfInfoTypes + _countof(NoNfInfoTypes), ft) == NoNfInfoTypes + _countof(NoNfInfoTypes) );
}

// ����� ������� ������ � ������ �����
namespace lighthouse_ra {
   int const RaconIsAbsent          = 0x01;
   int const RaconIsAvailable       = 0x02;
   int const RaconIsAbsentInSea     = 0x03;
   int const RaconIsAvailableInSea  = 0x04;

   int const RangeIsAvailable = 0x80;  // ������� ������
}

// ��� ������� ������ �����
namespace lighthouse_tp {
   int const Undefined           = 1;  // �� ����������
   int const NorthMark           = 2;  // ��������
   int const SouthMark           = 3;  // �����
   int const EastMark            = 4;  // ���������
   int const WestMark            = 5;  // ��������
   int const IsolatedDanger      = 6;  // ��� ����������
   int const PortHandMark        = 7;  // �����
   int const StarboardHandMark   = 8;  // ������
   int const SpecialMark         = 9;  // ������������ ����������
   int const SafeWaterMark       = 10; // �������� ���������
}

//////////////////////////////////////////////////////////////////////////
// ���� ���� ���/������
namespace light_color {
   char const NoLight = 0;
   char const Red     = 1;
   char const Green   = 2;
   char const White   = 3;
   char const Blue    = 4;
   char const Yellow  = 5;
   char const Violet  = 6;
   char const Amber   = 7;
   char const Orange  = 8;
}

// ��� ���
namespace buoy_tp {
   int const Buoy                 = 1; 
   int const NorthCardinalBuoy    = 2; 
   int const SouthCardinalBuoy    = 3; 
   int const EastCardinalBuoy     = 4; 
   int const WestCardinalBuoy     = 5; 
   int const Beacon               = 6; 
   int const SparBuoy             = 7; 
   int const IsolatedDangerBuoy   = 8; 
   int const PortHandBuoy         = 9; 
   int const StarboardHandBuoy    = 10;
   int const SpecialBuoy          = 11;
   int const SafeWaterBuoy        = 12;
   int const Platform             = 13;
   int const NorthCardinalBeacon  = 14;
   int const SouthCardinalBeacon  = 15;
   int const EastCardinalBeacon   = 16;
   int const WestCardinalBeacon   = 17;
   int const IsolatedDangerBeacon = 18;
   int const PortHandBeacon       = 19;
   int const StarboardHandBeacon  = 20;
   int const SpecialPurposeBeacon = 21;
   int const MooringBuoy          = 22;
   int const FixedPoint           = 23;
   int const Pole                 = 24;
   int const Cairn                = 25;
}

}