PGDMP                     	    w         	   telemetry    12.0    12.0 �    �           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                      false            �           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                      false            �           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                      false            �           1262    16393 	   telemetry    DATABASE     �   CREATE DATABASE telemetry WITH TEMPLATE = template0 ENCODING = 'UTF8' LC_COLLATE = 'Russian_Russia.1252' LC_CTYPE = 'Russian_Russia.1252';
    DROP DATABASE telemetry;
                postgres    false            �            1259    16414    air_track_predicted_strob    TABLE     h  CREATE TABLE public.air_track_predicted_strob (
    "AirTrackPredicted" integer NOT NULL,
    "minDistance" real,
    "maxDistance" real,
    "minRadialVelocity" real,
    "maxRadialVelocity" real,
    "lastTimeUpdate" real,
    "sigmaDistance" real,
    "sigmaVelocity" real,
    "sigmaEpsilon" real,
    "sigmaBetta" real,
    "AirTrack" integer NOT NULL
);
 -   DROP TABLE public.air_track_predicted_strob;
       public         heap    postgres    false            �            1259    16410 ,   AirTrackPredictedStrob_AirTrackPredicted_seq    SEQUENCE     �   CREATE SEQUENCE public."AirTrackPredictedStrob_AirTrackPredicted_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 E   DROP SEQUENCE public."AirTrackPredictedStrob_AirTrackPredicted_seq";
       public          postgres    false    207            �           0    0 ,   AirTrackPredictedStrob_AirTrackPredicted_seq    SEQUENCE OWNED BY     �   ALTER SEQUENCE public."AirTrackPredictedStrob_AirTrackPredicted_seq" OWNED BY public.air_track_predicted_strob."AirTrackPredicted";
          public          postgres    false    206            �            1259    16563    air_tracks_ids    TABLE     {   CREATE TABLE public.air_tracks_ids (
    "TrackId" integer NOT NULL,
    "AirTrack" integer NOT NULL,
    "taskId" real
);
 "   DROP TABLE public.air_tracks_ids;
       public         heap    postgres    false            �            1259    16559    AirTracksIds_TrackId_seq    SEQUENCE     �   CREATE SEQUENCE public."AirTracksIds_TrackId_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 1   DROP SEQUENCE public."AirTracksIds_TrackId_seq";
       public          postgres    false    230            �           0    0    AirTracksIds_TrackId_seq    SEQUENCE OWNED BY     [   ALTER SEQUENCE public."AirTracksIds_TrackId_seq" OWNED BY public.air_tracks_ids."TrackId";
          public          postgres    false    228            �            1259    16561    AirTracksIds_pkAirTrack_seq    SEQUENCE     �   CREATE SEQUENCE public."AirTracksIds_pkAirTrack_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 4   DROP SEQUENCE public."AirTracksIds_pkAirTrack_seq";
       public          postgres    false    230            �           0    0    AirTracksIds_pkAirTrack_seq    SEQUENCE OWNED BY     _   ALTER SEQUENCE public."AirTracksIds_pkAirTrack_seq" OWNED BY public.air_tracks_ids."AirTrack";
          public          postgres    false    229            �            1259    16508 
   air_tracks    TABLE     �  CREATE TABLE public.air_tracks (
    "AirTrack" integer NOT NULL,
    "Candidate" integer NOT NULL,
    "MarkId" integer NOT NULL,
    "trackType" real,
    priority real,
    "antennaId" real,
    "epsilonBSK" real,
    "bettaBSK" real,
    "pulsePeriod" real,
    "nextTimeUpdate" real,
    distance real,
    "radialVelocity" real,
    "missisCount" real,
    "scanPeriod" real
);
    DROP TABLE public.air_tracks;
       public         heap    postgres    false            �            1259    16502    AirTracks_AirTrack_seq    SEQUENCE     �   CREATE SEQUENCE public."AirTracks_AirTrack_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 /   DROP SEQUENCE public."AirTracks_AirTrack_seq";
       public          postgres    false    221            �           0    0    AirTracks_AirTrack_seq    SEQUENCE OWNED BY     V   ALTER SEQUENCE public."AirTracks_AirTrack_seq" OWNED BY public.air_tracks."AirTrack";
          public          postgres    false    218            �            1259    16504    AirTracks_pkCandidate_seq    SEQUENCE     �   CREATE SEQUENCE public."AirTracks_pkCandidate_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 2   DROP SEQUENCE public."AirTracks_pkCandidate_seq";
       public          postgres    false    221            �           0    0    AirTracks_pkCandidate_seq    SEQUENCE OWNED BY     Z   ALTER SEQUENCE public."AirTracks_pkCandidate_seq" OWNED BY public.air_tracks."Candidate";
          public          postgres    false    219            �            1259    16506    AirTracks_pkMark_seq    SEQUENCE     �   CREATE SEQUENCE public."AirTracks_pkMark_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 -   DROP SEQUENCE public."AirTracks_pkMark_seq";
       public          postgres    false    221            �           0    0    AirTracks_pkMark_seq    SEQUENCE OWNED BY     R   ALTER SEQUENCE public."AirTracks_pkMark_seq" OWNED BY public.air_tracks."MarkId";
          public          postgres    false    220            �            1259    16396 
   beam_tasks    TABLE     �  CREATE TABLE public.beam_tasks (
    "BeamTask" integer NOT NULL,
    "taskId" integer,
    "taskType" integer,
    "pulsePeriod" real,
    "antennaId" integer,
    "epsilonBSK" real,
    "bettaBSK" real,
    "lowerDistanceTrim" real,
    "upperDistanceTrim" real,
    "upperVelocityTrim" real,
    "lowerVelocityTrim" real,
    "isFake" boolean,
    "techPointDistance" real,
    "techPointHarmonic" real,
    treshold real
);
    DROP TABLE public.beam_tasks;
       public         heap    postgres    false            �            1259    16394    BeamTasks_BeamTask_seq    SEQUENCE     �   CREATE SEQUENCE public."BeamTasks_BeamTask_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 /   DROP SEQUENCE public."BeamTasks_BeamTask_seq";
       public          postgres    false    203            �           0    0    BeamTasks_BeamTask_seq    SEQUENCE OWNED BY     V   ALTER SEQUENCE public."BeamTasks_BeamTask_seq" OWNED BY public.beam_tasks."BeamTask";
          public          postgres    false    202            �            1259    16531    candidates_ids    TABLE     �   CREATE TABLE public.candidates_ids (
    "CandidateIds" integer NOT NULL,
    "Candidate" integer NOT NULL,
    "candidateId" real
);
 "   DROP TABLE public.candidates_ids;
       public         heap    postgres    false            �            1259    16527    CandidatesIds_CandidateIds_seq    SEQUENCE     �   CREATE SEQUENCE public."CandidatesIds_CandidateIds_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 7   DROP SEQUENCE public."CandidatesIds_CandidateIds_seq";
       public          postgres    false    224            �           0    0    CandidatesIds_CandidateIds_seq    SEQUENCE OWNED BY     f   ALTER SEQUENCE public."CandidatesIds_CandidateIds_seq" OWNED BY public.candidates_ids."CandidateIds";
          public          postgres    false    222            �            1259    16529    CandidatesIds_pkCandidates_seq    SEQUENCE     �   CREATE SEQUENCE public."CandidatesIds_pkCandidates_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 7   DROP SEQUENCE public."CandidatesIds_pkCandidates_seq";
       public          postgres    false    224            �           0    0    CandidatesIds_pkCandidates_seq    SEQUENCE OWNED BY     c   ALTER SEQUENCE public."CandidatesIds_pkCandidates_seq" OWNED BY public.candidates_ids."Candidate";
          public          postgres    false    223            �            1259    16466 
   candidates    TABLE     O  CREATE TABLE public.candidates (
    "Candidate" integer NOT NULL,
    "epsilonBSK" real,
    "bettaBSK" real,
    state real,
    "numDistanceZone" real,
    "numVelocityZone" real,
    "distanceZoneWeight" real,
    "velocityZoneWeight" real,
    "timeUpdated" real,
    "MarkId" integer NOT NULL,
    "BeamTask" integer NOT NULL
);
    DROP TABLE public.candidates;
       public         heap    postgres    false            �            1259    16464    Candidates_Candidate_seq    SEQUENCE     �   CREATE SEQUENCE public."Candidates_Candidate_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 1   DROP SEQUENCE public."Candidates_Candidate_seq";
       public          postgres    false    215            �           0    0    Candidates_Candidate_seq    SEQUENCE OWNED BY     Y   ALTER SEQUENCE public."Candidates_Candidate_seq" OWNED BY public.candidates."Candidate";
          public          postgres    false    214            �            1259    16479    Candidates_pkBeamTaskId_seq    SEQUENCE     �   CREATE SEQUENCE public."Candidates_pkBeamTaskId_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 4   DROP SEQUENCE public."Candidates_pkBeamTaskId_seq";
       public          postgres    false    215            �           0    0    Candidates_pkBeamTaskId_seq    SEQUENCE OWNED BY     [   ALTER SEQUENCE public."Candidates_pkBeamTaskId_seq" OWNED BY public.candidates."BeamTask";
          public          postgres    false    217            �            1259    16472    Candidates_pkMarkId_seq    SEQUENCE     �   CREATE SEQUENCE public."Candidates_pkMarkId_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 0   DROP SEQUENCE public."Candidates_pkMarkId_seq";
       public          postgres    false    215            �           0    0    Candidates_pkMarkId_seq    SEQUENCE OWNED BY     U   ALTER SEQUENCE public."Candidates_pkMarkId_seq" OWNED BY public.candidates."MarkId";
          public          postgres    false    216            �            1259    16579    forbidden_sector_ids    TABLE        CREATE TABLE public.forbidden_sector_ids (
    "ForbiddenSectorId" integer NOT NULL,
    "ForbiddenSector" integer NOT NULL
);
 (   DROP TABLE public.forbidden_sector_ids;
       public         heap    postgres    false            �            1259    16575 (   ForbiddenSectorIds_ForbiddenSectorId_seq    SEQUENCE     �   CREATE SEQUENCE public."ForbiddenSectorIds_ForbiddenSectorId_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 A   DROP SEQUENCE public."ForbiddenSectorIds_ForbiddenSectorId_seq";
       public          postgres    false    233            �           0    0 (   ForbiddenSectorIds_ForbiddenSectorId_seq    SEQUENCE OWNED BY     {   ALTER SEQUENCE public."ForbiddenSectorIds_ForbiddenSectorId_seq" OWNED BY public.forbidden_sector_ids."ForbiddenSectorId";
          public          postgres    false    231            �            1259    16577 (   ForbiddenSectorIds_pkForbiddenSector_seq    SEQUENCE     �   CREATE SEQUENCE public."ForbiddenSectorIds_pkForbiddenSector_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 A   DROP SEQUENCE public."ForbiddenSectorIds_pkForbiddenSector_seq";
       public          postgres    false    233            �           0    0 (   ForbiddenSectorIds_pkForbiddenSector_seq    SEQUENCE OWNED BY     y   ALTER SEQUENCE public."ForbiddenSectorIds_pkForbiddenSector_seq" OWNED BY public.forbidden_sector_ids."ForbiddenSector";
          public          postgres    false    232            �            1259    16404    forbidden_sectors    TABLE       CREATE TABLE public.forbidden_sectors (
    "ForbiddenSector" integer NOT NULL,
    "forbiddenSectorId" integer,
    "azimuthBeginNSSK" real,
    "azimuthEndNSSK" real,
    "elevationBeginNSSK" real,
    "elevetionEndNSSK" real,
    "lastTimeUpdate" real,
    "isActive" boolean
);
 %   DROP TABLE public.forbidden_sectors;
       public         heap    postgres    false            �            1259    16402 $   ForbiddenSectors_ForbiddenSector_seq    SEQUENCE     �   CREATE SEQUENCE public."ForbiddenSectors_ForbiddenSector_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 =   DROP SEQUENCE public."ForbiddenSectors_ForbiddenSector_seq";
       public          postgres    false    205            �           0    0 $   ForbiddenSectors_ForbiddenSector_seq    SEQUENCE OWNED BY     r   ALTER SEQUENCE public."ForbiddenSectors_ForbiddenSector_seq" OWNED BY public.forbidden_sectors."ForbiddenSector";
          public          postgres    false    204            �            1259    16425    primary_marks    TABLE     >  CREATE TABLE public.primary_marks (
    "MarkId" integer NOT NULL,
    "BeamTask" integer NOT NULL,
    distance real,
    "dopplerSpeed" real,
    azimuth real,
    elevation real,
    "signalLevel" real,
    "reflectedEnergy" real,
    type integer,
    beta real,
    epsilon real,
    "hasMatchedTrack" boolean
);
 !   DROP TABLE public.primary_marks;
       public         heap    postgres    false            �            1259    16421    PrimaryMarks_PrimaryMark_seq    SEQUENCE     �   CREATE SEQUENCE public."PrimaryMarks_PrimaryMark_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 5   DROP SEQUENCE public."PrimaryMarks_PrimaryMark_seq";
       public          postgres    false    210            �           0    0    PrimaryMarks_PrimaryMark_seq    SEQUENCE OWNED BY     ]   ALTER SEQUENCE public."PrimaryMarks_PrimaryMark_seq" OWNED BY public.primary_marks."MarkId";
          public          postgres    false    208            �            1259    16423    PrimaryMarks_pkBeamTaskId_seq    SEQUENCE     �   CREATE SEQUENCE public."PrimaryMarks_pkBeamTaskId_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 6   DROP SEQUENCE public."PrimaryMarks_pkBeamTaskId_seq";
       public          postgres    false    210            �           0    0    PrimaryMarks_pkBeamTaskId_seq    SEQUENCE OWNED BY     `   ALTER SEQUENCE public."PrimaryMarks_pkBeamTaskId_seq" OWNED BY public.primary_marks."BeamTask";
          public          postgres    false    209            �            1259    16547    view_directions_ids    TABLE     �   CREATE TABLE public.view_directions_ids (
    "ViewDirectionId" integer NOT NULL,
    "ViewDirection" integer NOT NULL,
    "directionId" real
);
 '   DROP TABLE public.view_directions_ids;
       public         heap    postgres    false            �            1259    16543 %   ViewDirectionsIds_ViewDirectionId_seq    SEQUENCE     �   CREATE SEQUENCE public."ViewDirectionsIds_ViewDirectionId_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 >   DROP SEQUENCE public."ViewDirectionsIds_ViewDirectionId_seq";
       public          postgres    false    227            �           0    0 %   ViewDirectionsIds_ViewDirectionId_seq    SEQUENCE OWNED BY     u   ALTER SEQUENCE public."ViewDirectionsIds_ViewDirectionId_seq" OWNED BY public.view_directions_ids."ViewDirectionId";
          public          postgres    false    225            �            1259    16545 '   ViewDirectionsIds_pkViewDirectionId_seq    SEQUENCE     �   CREATE SEQUENCE public."ViewDirectionsIds_pkViewDirectionId_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 @   DROP SEQUENCE public."ViewDirectionsIds_pkViewDirectionId_seq";
       public          postgres    false    227            �           0    0 '   ViewDirectionsIds_pkViewDirectionId_seq    SEQUENCE OWNED BY     u   ALTER SEQUENCE public."ViewDirectionsIds_pkViewDirectionId_seq" OWNED BY public.view_directions_ids."ViewDirection";
          public          postgres    false    226            �            1259    16436    view_directions    TABLE     �   CREATE TABLE public.view_directions (
    "ViewDirection" integer NOT NULL,
    "directionAzimuthNSSK" real,
    "directionElevationNSSK" real,
    "antennaId" integer,
    "scanPeriod" real,
    "lastTimeUpdate" real,
    "BeamTask" integer
);
 #   DROP TABLE public.view_directions;
       public         heap    postgres    false            �            1259    16432     ViewDirections_ViewDirection_seq    SEQUENCE     �   CREATE SEQUENCE public."ViewDirections_ViewDirection_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 9   DROP SEQUENCE public."ViewDirections_ViewDirection_seq";
       public          postgres    false    212            �           0    0     ViewDirections_ViewDirection_seq    SEQUENCE OWNED BY     j   ALTER SEQUENCE public."ViewDirections_ViewDirection_seq" OWNED BY public.view_directions."ViewDirection";
          public          postgres    false    211            �            1259    16457    air_track_periods    TABLE     �   CREATE TABLE public.air_track_periods (
    "AirTrackPeriods" integer NOT NULL,
    "AirTrack" integer NOT NULL,
    "pulsePeriod" real
);
 %   DROP TABLE public.air_track_periods;
       public         heap    postgres    false            �            1259    16598    air_track_periods_AirTrack_seq    SEQUENCE     �   CREATE SEQUENCE public."air_track_periods_AirTrack_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 7   DROP SEQUENCE public."air_track_periods_AirTrack_seq";
       public          postgres    false    213            �           0    0    air_track_periods_AirTrack_seq    SEQUENCE OWNED BY     e   ALTER SEQUENCE public."air_track_periods_AirTrack_seq" OWNED BY public.air_track_periods."AirTrack";
          public          postgres    false    235            �            1259    16592 '   air_track_periods_pkAirTrackPeriods_seq    SEQUENCE     �   CREATE SEQUENCE public."air_track_periods_pkAirTrackPeriods_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 @   DROP SEQUENCE public."air_track_periods_pkAirTrackPeriods_seq";
       public          postgres    false    213            �           0    0 '   air_track_periods_pkAirTrackPeriods_seq    SEQUENCE OWNED BY     u   ALTER SEQUENCE public."air_track_periods_pkAirTrackPeriods_seq" OWNED BY public.air_track_periods."AirTrackPeriods";
          public          postgres    false    234            �            1259    16616 &   air_track_predicted_strob_AirTrack_seq    SEQUENCE     �   CREATE SEQUENCE public."air_track_predicted_strob_AirTrack_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 ?   DROP SEQUENCE public."air_track_predicted_strob_AirTrack_seq";
       public          postgres    false    207            �           0    0 &   air_track_predicted_strob_AirTrack_seq    SEQUENCE OWNED BY     u   ALTER SEQUENCE public."air_track_predicted_strob_AirTrack_seq" OWNED BY public.air_track_predicted_strob."AirTrack";
          public          postgres    false    236            �
           2604    16594 !   air_track_periods AirTrackPeriods    DEFAULT     �   ALTER TABLE ONLY public.air_track_periods ALTER COLUMN "AirTrackPeriods" SET DEFAULT nextval('public."air_track_periods_pkAirTrackPeriods_seq"'::regclass);
 R   ALTER TABLE public.air_track_periods ALTER COLUMN "AirTrackPeriods" DROP DEFAULT;
       public          postgres    false    234    213            �
           2604    16600    air_track_periods AirTrack    DEFAULT     �   ALTER TABLE ONLY public.air_track_periods ALTER COLUMN "AirTrack" SET DEFAULT nextval('public."air_track_periods_AirTrack_seq"'::regclass);
 K   ALTER TABLE public.air_track_periods ALTER COLUMN "AirTrack" DROP DEFAULT;
       public          postgres    false    235    213            �
           2604    16417 +   air_track_predicted_strob AirTrackPredicted    DEFAULT     �   ALTER TABLE ONLY public.air_track_predicted_strob ALTER COLUMN "AirTrackPredicted" SET DEFAULT nextval('public."AirTrackPredictedStrob_AirTrackPredicted_seq"'::regclass);
 \   ALTER TABLE public.air_track_predicted_strob ALTER COLUMN "AirTrackPredicted" DROP DEFAULT;
       public          postgres    false    206    207    207            �
           2604    16618 "   air_track_predicted_strob AirTrack    DEFAULT     �   ALTER TABLE ONLY public.air_track_predicted_strob ALTER COLUMN "AirTrack" SET DEFAULT nextval('public."air_track_predicted_strob_AirTrack_seq"'::regclass);
 S   ALTER TABLE public.air_track_predicted_strob ALTER COLUMN "AirTrack" DROP DEFAULT;
       public          postgres    false    236    207            �
           2604    16511    air_tracks AirTrack    DEFAULT     }   ALTER TABLE ONLY public.air_tracks ALTER COLUMN "AirTrack" SET DEFAULT nextval('public."AirTracks_AirTrack_seq"'::regclass);
 D   ALTER TABLE public.air_tracks ALTER COLUMN "AirTrack" DROP DEFAULT;
       public          postgres    false    221    218    221            �
           2604    16512    air_tracks Candidate    DEFAULT     �   ALTER TABLE ONLY public.air_tracks ALTER COLUMN "Candidate" SET DEFAULT nextval('public."AirTracks_pkCandidate_seq"'::regclass);
 E   ALTER TABLE public.air_tracks ALTER COLUMN "Candidate" DROP DEFAULT;
       public          postgres    false    219    221    221            �
           2604    16513    air_tracks MarkId    DEFAULT     y   ALTER TABLE ONLY public.air_tracks ALTER COLUMN "MarkId" SET DEFAULT nextval('public."AirTracks_pkMark_seq"'::regclass);
 B   ALTER TABLE public.air_tracks ALTER COLUMN "MarkId" DROP DEFAULT;
       public          postgres    false    220    221    221            �
           2604    16566    air_tracks_ids TrackId    DEFAULT     �   ALTER TABLE ONLY public.air_tracks_ids ALTER COLUMN "TrackId" SET DEFAULT nextval('public."AirTracksIds_TrackId_seq"'::regclass);
 G   ALTER TABLE public.air_tracks_ids ALTER COLUMN "TrackId" DROP DEFAULT;
       public          postgres    false    228    230    230            �
           2604    16567    air_tracks_ids AirTrack    DEFAULT     �   ALTER TABLE ONLY public.air_tracks_ids ALTER COLUMN "AirTrack" SET DEFAULT nextval('public."AirTracksIds_pkAirTrack_seq"'::regclass);
 H   ALTER TABLE public.air_tracks_ids ALTER COLUMN "AirTrack" DROP DEFAULT;
       public          postgres    false    229    230    230            �
           2604    16399    beam_tasks BeamTask    DEFAULT     }   ALTER TABLE ONLY public.beam_tasks ALTER COLUMN "BeamTask" SET DEFAULT nextval('public."BeamTasks_BeamTask_seq"'::regclass);
 D   ALTER TABLE public.beam_tasks ALTER COLUMN "BeamTask" DROP DEFAULT;
       public          postgres    false    203    202    203            �
           2604    16469    candidates Candidate    DEFAULT     �   ALTER TABLE ONLY public.candidates ALTER COLUMN "Candidate" SET DEFAULT nextval('public."Candidates_Candidate_seq"'::regclass);
 E   ALTER TABLE public.candidates ALTER COLUMN "Candidate" DROP DEFAULT;
       public          postgres    false    214    215    215            �
           2604    16474    candidates MarkId    DEFAULT     |   ALTER TABLE ONLY public.candidates ALTER COLUMN "MarkId" SET DEFAULT nextval('public."Candidates_pkMarkId_seq"'::regclass);
 B   ALTER TABLE public.candidates ALTER COLUMN "MarkId" DROP DEFAULT;
       public          postgres    false    216    215            �
           2604    16481    candidates BeamTask    DEFAULT     �   ALTER TABLE ONLY public.candidates ALTER COLUMN "BeamTask" SET DEFAULT nextval('public."Candidates_pkBeamTaskId_seq"'::regclass);
 D   ALTER TABLE public.candidates ALTER COLUMN "BeamTask" DROP DEFAULT;
       public          postgres    false    217    215            �
           2604    16534    candidates_ids CandidateIds    DEFAULT     �   ALTER TABLE ONLY public.candidates_ids ALTER COLUMN "CandidateIds" SET DEFAULT nextval('public."CandidatesIds_CandidateIds_seq"'::regclass);
 L   ALTER TABLE public.candidates_ids ALTER COLUMN "CandidateIds" DROP DEFAULT;
       public          postgres    false    224    222    224            �
           2604    16535    candidates_ids Candidate    DEFAULT     �   ALTER TABLE ONLY public.candidates_ids ALTER COLUMN "Candidate" SET DEFAULT nextval('public."CandidatesIds_pkCandidates_seq"'::regclass);
 I   ALTER TABLE public.candidates_ids ALTER COLUMN "Candidate" DROP DEFAULT;
       public          postgres    false    224    223    224            �
           2604    16582 &   forbidden_sector_ids ForbiddenSectorId    DEFAULT     �   ALTER TABLE ONLY public.forbidden_sector_ids ALTER COLUMN "ForbiddenSectorId" SET DEFAULT nextval('public."ForbiddenSectorIds_ForbiddenSectorId_seq"'::regclass);
 W   ALTER TABLE public.forbidden_sector_ids ALTER COLUMN "ForbiddenSectorId" DROP DEFAULT;
       public          postgres    false    233    231    233            �
           2604    16583 $   forbidden_sector_ids ForbiddenSector    DEFAULT     �   ALTER TABLE ONLY public.forbidden_sector_ids ALTER COLUMN "ForbiddenSector" SET DEFAULT nextval('public."ForbiddenSectorIds_pkForbiddenSector_seq"'::regclass);
 U   ALTER TABLE public.forbidden_sector_ids ALTER COLUMN "ForbiddenSector" DROP DEFAULT;
       public          postgres    false    233    232    233            �
           2604    16407 !   forbidden_sectors ForbiddenSector    DEFAULT     �   ALTER TABLE ONLY public.forbidden_sectors ALTER COLUMN "ForbiddenSector" SET DEFAULT nextval('public."ForbiddenSectors_ForbiddenSector_seq"'::regclass);
 R   ALTER TABLE public.forbidden_sectors ALTER COLUMN "ForbiddenSector" DROP DEFAULT;
       public          postgres    false    204    205    205            �
           2604    16428    primary_marks MarkId    DEFAULT     �   ALTER TABLE ONLY public.primary_marks ALTER COLUMN "MarkId" SET DEFAULT nextval('public."PrimaryMarks_PrimaryMark_seq"'::regclass);
 E   ALTER TABLE public.primary_marks ALTER COLUMN "MarkId" DROP DEFAULT;
       public          postgres    false    210    208    210            �
           2604    16429    primary_marks BeamTask    DEFAULT     �   ALTER TABLE ONLY public.primary_marks ALTER COLUMN "BeamTask" SET DEFAULT nextval('public."PrimaryMarks_pkBeamTaskId_seq"'::regclass);
 G   ALTER TABLE public.primary_marks ALTER COLUMN "BeamTask" DROP DEFAULT;
       public          postgres    false    209    210    210            �
           2604    16439    view_directions ViewDirection    DEFAULT     �   ALTER TABLE ONLY public.view_directions ALTER COLUMN "ViewDirection" SET DEFAULT nextval('public."ViewDirections_ViewDirection_seq"'::regclass);
 N   ALTER TABLE public.view_directions ALTER COLUMN "ViewDirection" DROP DEFAULT;
       public          postgres    false    211    212    212            �
           2604    16550 #   view_directions_ids ViewDirectionId    DEFAULT     �   ALTER TABLE ONLY public.view_directions_ids ALTER COLUMN "ViewDirectionId" SET DEFAULT nextval('public."ViewDirectionsIds_ViewDirectionId_seq"'::regclass);
 T   ALTER TABLE public.view_directions_ids ALTER COLUMN "ViewDirectionId" DROP DEFAULT;
       public          postgres    false    225    227    227            �
           2604    16551 !   view_directions_ids ViewDirection    DEFAULT     �   ALTER TABLE ONLY public.view_directions_ids ALTER COLUMN "ViewDirection" SET DEFAULT nextval('public."ViewDirectionsIds_pkViewDirectionId_seq"'::regclass);
 R   ALTER TABLE public.view_directions_ids ALTER COLUMN "ViewDirection" DROP DEFAULT;
       public          postgres    false    226    227    227            �          0    16457    air_track_periods 
   TABLE DATA           Y   COPY public.air_track_periods ("AirTrackPeriods", "AirTrack", "pulsePeriod") FROM stdin;
    public          postgres    false    213   q�       �          0    16414    air_track_predicted_strob 
   TABLE DATA           �   COPY public.air_track_predicted_strob ("AirTrackPredicted", "minDistance", "maxDistance", "minRadialVelocity", "maxRadialVelocity", "lastTimeUpdate", "sigmaDistance", "sigmaVelocity", "sigmaEpsilon", "sigmaBetta", "AirTrack") FROM stdin;
    public          postgres    false    207   ��       �          0    16508 
   air_tracks 
   TABLE DATA           �   COPY public.air_tracks ("AirTrack", "Candidate", "MarkId", "trackType", priority, "antennaId", "epsilonBSK", "bettaBSK", "pulsePeriod", "nextTimeUpdate", distance, "radialVelocity", "missisCount", "scanPeriod") FROM stdin;
    public          postgres    false    221   ��       �          0    16563    air_tracks_ids 
   TABLE DATA           I   COPY public.air_tracks_ids ("TrackId", "AirTrack", "taskId") FROM stdin;
    public          postgres    false    230   ȿ       �          0    16396 
   beam_tasks 
   TABLE DATA             COPY public.beam_tasks ("BeamTask", "taskId", "taskType", "pulsePeriod", "antennaId", "epsilonBSK", "bettaBSK", "lowerDistanceTrim", "upperDistanceTrim", "upperVelocityTrim", "lowerVelocityTrim", "isFake", "techPointDistance", "techPointHarmonic", treshold) FROM stdin;
    public          postgres    false    203   �       �          0    16466 
   candidates 
   TABLE DATA           �   COPY public.candidates ("Candidate", "epsilonBSK", "bettaBSK", state, "numDistanceZone", "numVelocityZone", "distanceZoneWeight", "velocityZoneWeight", "timeUpdated", "MarkId", "BeamTask") FROM stdin;
    public          postgres    false    215   �       �          0    16531    candidates_ids 
   TABLE DATA           T   COPY public.candidates_ids ("CandidateIds", "Candidate", "candidateId") FROM stdin;
    public          postgres    false    224   �       �          0    16579    forbidden_sector_ids 
   TABLE DATA           V   COPY public.forbidden_sector_ids ("ForbiddenSectorId", "ForbiddenSector") FROM stdin;
    public          postgres    false    233   <�       �          0    16404    forbidden_sectors 
   TABLE DATA           �   COPY public.forbidden_sectors ("ForbiddenSector", "forbiddenSectorId", "azimuthBeginNSSK", "azimuthEndNSSK", "elevationBeginNSSK", "elevetionEndNSSK", "lastTimeUpdate", "isActive") FROM stdin;
    public          postgres    false    205   Y�       �          0    16425    primary_marks 
   TABLE DATA           �   COPY public.primary_marks ("MarkId", "BeamTask", distance, "dopplerSpeed", azimuth, elevation, "signalLevel", "reflectedEnergy", type, beta, epsilon, "hasMatchedTrack") FROM stdin;
    public          postgres    false    210   v�       �          0    16436    view_directions 
   TABLE DATA           �   COPY public.view_directions ("ViewDirection", "directionAzimuthNSSK", "directionElevationNSSK", "antennaId", "scanPeriod", "lastTimeUpdate", "BeamTask") FROM stdin;
    public          postgres    false    212   ��       �          0    16547    view_directions_ids 
   TABLE DATA           `   COPY public.view_directions_ids ("ViewDirectionId", "ViewDirection", "directionId") FROM stdin;
    public          postgres    false    227   ��       �           0    0 ,   AirTrackPredictedStrob_AirTrackPredicted_seq    SEQUENCE SET     ]   SELECT pg_catalog.setval('public."AirTrackPredictedStrob_AirTrackPredicted_seq"', 1, false);
          public          postgres    false    206            �           0    0    AirTracksIds_TrackId_seq    SEQUENCE SET     I   SELECT pg_catalog.setval('public."AirTracksIds_TrackId_seq"', 1, false);
          public          postgres    false    228            �           0    0    AirTracksIds_pkAirTrack_seq    SEQUENCE SET     L   SELECT pg_catalog.setval('public."AirTracksIds_pkAirTrack_seq"', 1, false);
          public          postgres    false    229            �           0    0    AirTracks_AirTrack_seq    SEQUENCE SET     G   SELECT pg_catalog.setval('public."AirTracks_AirTrack_seq"', 1, false);
          public          postgres    false    218            �           0    0    AirTracks_pkCandidate_seq    SEQUENCE SET     J   SELECT pg_catalog.setval('public."AirTracks_pkCandidate_seq"', 1, false);
          public          postgres    false    219            �           0    0    AirTracks_pkMark_seq    SEQUENCE SET     E   SELECT pg_catalog.setval('public."AirTracks_pkMark_seq"', 1, false);
          public          postgres    false    220            �           0    0    BeamTasks_BeamTask_seq    SEQUENCE SET     G   SELECT pg_catalog.setval('public."BeamTasks_BeamTask_seq"', 1, false);
          public          postgres    false    202            �           0    0    CandidatesIds_CandidateIds_seq    SEQUENCE SET     O   SELECT pg_catalog.setval('public."CandidatesIds_CandidateIds_seq"', 1, false);
          public          postgres    false    222            �           0    0    CandidatesIds_pkCandidates_seq    SEQUENCE SET     O   SELECT pg_catalog.setval('public."CandidatesIds_pkCandidates_seq"', 1, false);
          public          postgres    false    223            �           0    0    Candidates_Candidate_seq    SEQUENCE SET     I   SELECT pg_catalog.setval('public."Candidates_Candidate_seq"', 1, false);
          public          postgres    false    214            �           0    0    Candidates_pkBeamTaskId_seq    SEQUENCE SET     L   SELECT pg_catalog.setval('public."Candidates_pkBeamTaskId_seq"', 1, false);
          public          postgres    false    217            �           0    0    Candidates_pkMarkId_seq    SEQUENCE SET     H   SELECT pg_catalog.setval('public."Candidates_pkMarkId_seq"', 1, false);
          public          postgres    false    216            �           0    0 (   ForbiddenSectorIds_ForbiddenSectorId_seq    SEQUENCE SET     Y   SELECT pg_catalog.setval('public."ForbiddenSectorIds_ForbiddenSectorId_seq"', 1, false);
          public          postgres    false    231            �           0    0 (   ForbiddenSectorIds_pkForbiddenSector_seq    SEQUENCE SET     Y   SELECT pg_catalog.setval('public."ForbiddenSectorIds_pkForbiddenSector_seq"', 1, false);
          public          postgres    false    232            �           0    0 $   ForbiddenSectors_ForbiddenSector_seq    SEQUENCE SET     U   SELECT pg_catalog.setval('public."ForbiddenSectors_ForbiddenSector_seq"', 1, false);
          public          postgres    false    204            �           0    0    PrimaryMarks_PrimaryMark_seq    SEQUENCE SET     M   SELECT pg_catalog.setval('public."PrimaryMarks_PrimaryMark_seq"', 1, false);
          public          postgres    false    208            �           0    0    PrimaryMarks_pkBeamTaskId_seq    SEQUENCE SET     N   SELECT pg_catalog.setval('public."PrimaryMarks_pkBeamTaskId_seq"', 1, false);
          public          postgres    false    209            �           0    0 %   ViewDirectionsIds_ViewDirectionId_seq    SEQUENCE SET     V   SELECT pg_catalog.setval('public."ViewDirectionsIds_ViewDirectionId_seq"', 1, false);
          public          postgres    false    225            �           0    0 '   ViewDirectionsIds_pkViewDirectionId_seq    SEQUENCE SET     X   SELECT pg_catalog.setval('public."ViewDirectionsIds_pkViewDirectionId_seq"', 1, false);
          public          postgres    false    226            �           0    0     ViewDirections_ViewDirection_seq    SEQUENCE SET     Q   SELECT pg_catalog.setval('public."ViewDirections_ViewDirection_seq"', 1, false);
          public          postgres    false    211            �           0    0    air_track_periods_AirTrack_seq    SEQUENCE SET     O   SELECT pg_catalog.setval('public."air_track_periods_AirTrack_seq"', 1, false);
          public          postgres    false    235            �           0    0 '   air_track_periods_pkAirTrackPeriods_seq    SEQUENCE SET     X   SELECT pg_catalog.setval('public."air_track_periods_pkAirTrackPeriods_seq"', 1, false);
          public          postgres    false    234            �           0    0 &   air_track_predicted_strob_AirTrack_seq    SEQUENCE SET     W   SELECT pg_catalog.setval('public."air_track_predicted_strob_AirTrack_seq"', 1, false);
          public          postgres    false    236                       2606    16569     air_tracks_ids AirTracksIds_pkey 
   CONSTRAINT     g   ALTER TABLE ONLY public.air_tracks_ids
    ADD CONSTRAINT "AirTracksIds_pkey" PRIMARY KEY ("TrackId");
 L   ALTER TABLE ONLY public.air_tracks_ids DROP CONSTRAINT "AirTracksIds_pkey";
       public            postgres    false    230            �
           2606    16515    air_tracks AirTracks_pkey 
   CONSTRAINT     a   ALTER TABLE ONLY public.air_tracks
    ADD CONSTRAINT "AirTracks_pkey" PRIMARY KEY ("AirTrack");
 E   ALTER TABLE ONLY public.air_tracks DROP CONSTRAINT "AirTracks_pkey";
       public            postgres    false    221            �
           2606    16401    beam_tasks BeamTasks_pkey 
   CONSTRAINT     a   ALTER TABLE ONLY public.beam_tasks
    ADD CONSTRAINT "BeamTasks_pkey" PRIMARY KEY ("BeamTask");
 E   ALTER TABLE ONLY public.beam_tasks DROP CONSTRAINT "BeamTasks_pkey";
       public            postgres    false    203                        2606    16537 !   candidates_ids CandidatesIds_pkey 
   CONSTRAINT     m   ALTER TABLE ONLY public.candidates_ids
    ADD CONSTRAINT "CandidatesIds_pkey" PRIMARY KEY ("CandidateIds");
 M   ALTER TABLE ONLY public.candidates_ids DROP CONSTRAINT "CandidatesIds_pkey";
       public            postgres    false    224            �
           2606    16471    candidates Candidates_pkey 
   CONSTRAINT     c   ALTER TABLE ONLY public.candidates
    ADD CONSTRAINT "Candidates_pkey" PRIMARY KEY ("Candidate");
 F   ALTER TABLE ONLY public.candidates DROP CONSTRAINT "Candidates_pkey";
       public            postgres    false    215                       2606    16585 ,   forbidden_sector_ids ForbiddenSectorIds_pkey 
   CONSTRAINT     }   ALTER TABLE ONLY public.forbidden_sector_ids
    ADD CONSTRAINT "ForbiddenSectorIds_pkey" PRIMARY KEY ("ForbiddenSectorId");
 X   ALTER TABLE ONLY public.forbidden_sector_ids DROP CONSTRAINT "ForbiddenSectorIds_pkey";
       public            postgres    false    233            �
           2606    16409 '   forbidden_sectors ForbiddenSectors_pkey 
   CONSTRAINT     v   ALTER TABLE ONLY public.forbidden_sectors
    ADD CONSTRAINT "ForbiddenSectors_pkey" PRIMARY KEY ("ForbiddenSector");
 S   ALTER TABLE ONLY public.forbidden_sectors DROP CONSTRAINT "ForbiddenSectors_pkey";
       public            postgres    false    205            �
           2606    16431    primary_marks PrimaryMarks_pkey 
   CONSTRAINT     e   ALTER TABLE ONLY public.primary_marks
    ADD CONSTRAINT "PrimaryMarks_pkey" PRIMARY KEY ("MarkId");
 K   ALTER TABLE ONLY public.primary_marks DROP CONSTRAINT "PrimaryMarks_pkey";
       public            postgres    false    210                       2606    16553 *   view_directions_ids ViewDirectionsIds_pkey 
   CONSTRAINT     y   ALTER TABLE ONLY public.view_directions_ids
    ADD CONSTRAINT "ViewDirectionsIds_pkey" PRIMARY KEY ("ViewDirectionId");
 V   ALTER TABLE ONLY public.view_directions_ids DROP CONSTRAINT "ViewDirectionsIds_pkey";
       public            postgres    false    227            �
           2606    16442 #   view_directions ViewDirections_pkey 
   CONSTRAINT     p   ALTER TABLE ONLY public.view_directions
    ADD CONSTRAINT "ViewDirections_pkey" PRIMARY KEY ("ViewDirection");
 O   ALTER TABLE ONLY public.view_directions DROP CONSTRAINT "ViewDirections_pkey";
       public            postgres    false    212            �
           2606    16610 (   air_track_periods air_track_periods_pkey 
   CONSTRAINT     u   ALTER TABLE ONLY public.air_track_periods
    ADD CONSTRAINT air_track_periods_pkey PRIMARY KEY ("AirTrackPeriods");
 R   ALTER TABLE ONLY public.air_track_periods DROP CONSTRAINT air_track_periods_pkey;
       public            postgres    false    213            �
           2606    16623 8   air_track_predicted_strob air_track_predicted_strob_pkey 
   CONSTRAINT     �   ALTER TABLE ONLY public.air_track_predicted_strob
    ADD CONSTRAINT air_track_predicted_strob_pkey PRIMARY KEY ("AirTrackPredicted");
 b   ALTER TABLE ONLY public.air_track_predicted_strob DROP CONSTRAINT air_track_predicted_strob_pkey;
       public            postgres    false    207            �
           1259    16491    fki_fkMarkId    INDEX     I   CREATE INDEX "fki_fkMarkId" ON public.candidates USING btree ("MarkId");
 "   DROP INDEX public."fki_fkMarkId";
       public            postgres    false    215                       2606    16570 +   air_tracks_ids AirTracksIds_pkAirTrack_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.air_tracks_ids
    ADD CONSTRAINT "AirTracksIds_pkAirTrack_fkey" FOREIGN KEY ("AirTrack") REFERENCES public.air_tracks("AirTrack") NOT VALID;
 W   ALTER TABLE ONLY public.air_tracks_ids DROP CONSTRAINT "AirTracksIds_pkAirTrack_fkey";
       public          postgres    false    230    221    2814                       2606    16517 %   air_tracks AirTracks_pkCandidate_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.air_tracks
    ADD CONSTRAINT "AirTracks_pkCandidate_fkey" FOREIGN KEY ("Candidate") REFERENCES public.candidates("Candidate") NOT VALID;
 Q   ALTER TABLE ONLY public.air_tracks DROP CONSTRAINT "AirTracks_pkCandidate_fkey";
       public          postgres    false    2811    221    215                       2606    16522     air_tracks AirTracks_pkMark_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.air_tracks
    ADD CONSTRAINT "AirTracks_pkMark_fkey" FOREIGN KEY ("MarkId") REFERENCES public.primary_marks("MarkId") NOT VALID;
 L   ALTER TABLE ONLY public.air_tracks DROP CONSTRAINT "AirTracks_pkMark_fkey";
       public          postgres    false    2805    221    210                       2606    16538 .   candidates_ids CandidatesIds_pkCandidates_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.candidates_ids
    ADD CONSTRAINT "CandidatesIds_pkCandidates_fkey" FOREIGN KEY ("Candidate") REFERENCES public.candidates("Candidate") NOT VALID;
 Z   ALTER TABLE ONLY public.candidates_ids DROP CONSTRAINT "CandidatesIds_pkCandidates_fkey";
       public          postgres    false    215    2811    224                       2606    16492 '   candidates Candidates_pkBeamTaskId_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.candidates
    ADD CONSTRAINT "Candidates_pkBeamTaskId_fkey" FOREIGN KEY ("BeamTask") REFERENCES public.beam_tasks("BeamTask") NOT VALID;
 S   ALTER TABLE ONLY public.candidates DROP CONSTRAINT "Candidates_pkBeamTaskId_fkey";
       public          postgres    false    203    215    2799                       2606    16497 #   candidates Candidates_pkMarkId_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.candidates
    ADD CONSTRAINT "Candidates_pkMarkId_fkey" FOREIGN KEY ("MarkId") REFERENCES public.primary_marks("MarkId") NOT VALID;
 O   ALTER TABLE ONLY public.candidates DROP CONSTRAINT "Candidates_pkMarkId_fkey";
       public          postgres    false    2805    210    215                       2606    16586 >   forbidden_sector_ids ForbiddenSectorIds_pkForbiddenSector_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.forbidden_sector_ids
    ADD CONSTRAINT "ForbiddenSectorIds_pkForbiddenSector_fkey" FOREIGN KEY ("ForbiddenSector") REFERENCES public.forbidden_sectors("ForbiddenSector") NOT VALID;
 j   ALTER TABLE ONLY public.forbidden_sector_ids DROP CONSTRAINT "ForbiddenSectorIds_pkForbiddenSector_fkey";
       public          postgres    false    2801    233    205                       2606    16554 <   view_directions_ids ViewDirectionsIds_pkViewDirectionId_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.view_directions_ids
    ADD CONSTRAINT "ViewDirectionsIds_pkViewDirectionId_fkey" FOREIGN KEY ("ViewDirection") REFERENCES public.view_directions("ViewDirection") NOT VALID;
 h   ALTER TABLE ONLY public.view_directions_ids DROP CONSTRAINT "ViewDirectionsIds_pkViewDirectionId_fkey";
       public          postgres    false    2807    227    212            
           2606    16604 1   air_track_periods air_track_periods_AirTrack_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.air_track_periods
    ADD CONSTRAINT "air_track_periods_AirTrack_fkey" FOREIGN KEY ("AirTrack") REFERENCES public.air_tracks("AirTrack") NOT VALID;
 ]   ALTER TABLE ONLY public.air_track_periods DROP CONSTRAINT "air_track_periods_AirTrack_fkey";
       public          postgres    false    213    221    2814                       2606    16624 A   air_track_predicted_strob air_track_predicted_strob_AirTrack_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.air_track_predicted_strob
    ADD CONSTRAINT "air_track_predicted_strob_AirTrack_fkey" FOREIGN KEY ("AirTrack") REFERENCES public.air_tracks("AirTrack") NOT VALID;
 m   ALTER TABLE ONLY public.air_track_predicted_strob DROP CONSTRAINT "air_track_predicted_strob_AirTrack_fkey";
       public          postgres    false    207    2814    221                       2606    24789 )   primary_marks primary_marks_BeamTask_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.primary_marks
    ADD CONSTRAINT "primary_marks_BeamTask_fkey" FOREIGN KEY ("BeamTask") REFERENCES public.beam_tasks("BeamTask") NOT VALID;
 U   ALTER TABLE ONLY public.primary_marks DROP CONSTRAINT "primary_marks_BeamTask_fkey";
       public          postgres    false    203    2799    210            	           2606    24784 -   view_directions view_directions_BeamTask_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.view_directions
    ADD CONSTRAINT "view_directions_BeamTask_fkey" FOREIGN KEY ("BeamTask") REFERENCES public.beam_tasks("BeamTask") NOT VALID;
 Y   ALTER TABLE ONLY public.view_directions DROP CONSTRAINT "view_directions_BeamTask_fkey";
       public          postgres    false    2799    203    212            �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �     