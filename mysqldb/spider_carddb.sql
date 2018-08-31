/*==============================================================*/
/* DBMS name:      MySQL 5.7.17                                 */
/* Created on:     2018-9-31 19£º25                             */
/*==============================================================*/
set names utf8;
drop database if  exists spider;
create database spider default character set utf8;
use spider;

drop table if exists baseinfo;
drop table if exists specdgroup;

/*==============================================================*/
/* Table: baseinfo                                              */
/*==============================================================*/
create table baseinfo
(id int  auto_increment primary key,
cdgroupname varchar(30),
profession char(2),
need int,
leixing char(2),
foreign key(cdgroupname) references specdgroup(cdgroupname)
)engine=innodb default charset=utf8;
/*==============================================================*/
/* Table: specdgroup                                            */
/*==============================================================*/
create table specdgroup
(cdgroupname char(10) primary key,
card1 varchar(10),
card2 varchar(10),
card3 varchar(10),
card4 varchar(10),
card5 varchar(10),
card6 varchar(10),
card7 varchar(10),
card8 varchar(10),
card9 varchar(10),
card10 varchar(10),
card11 varchar(10),
card12 varchar(10),
card13 varchar(10),
card14 varchar(10),
card15 varchar(10),
card16 varchar(10),
card17 varchar(10),
card18 varchar(10),
card19 varchar(10),
card20 varchar(10),
card21 varchar(10),
card22 varchar(10),
card23 varchar(10),
card24 varchar(10),
card25 varchar(10),
card26 varchar(10),
card27 varchar(10),
card28 varchar(10),
card29 varchar(10),
card30 varchar(10)
)engine=innodb default charset=utf8;