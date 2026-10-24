from chainbreaker.ingest.universal_adapters import parse_universal_log


def test_zeek_tsv_log_parser():
    zeek_log = """#separator \\x09
#set_separator	,
#empty_field	(empty)
#unset_field	-
#path	dns
#fields	ts	uid	id.orig_h	id.orig_p	id.resp_h	id.resp_p	proto	trans_id	rtt	query	qclass	qclass_name	qtype	qtype_name	rcode	rcode_name
1729735800.000000	CHhAvV3Gsnh4W8cvc3	10.0.1.50	5353	8.8.8.8	53	udp	34762	0.021000	malicious-beacon.org	1	C_INTERNET	1	A	0	NOERROR
#close	2026-10-24-02-10-00
"""
    rows = parse_universal_log(zeek_log)
    assert len(rows) == 1
    assert rows[0]["source"] == "dns"
    assert rows[0]["domain"] == "malicious-beacon.org"
    assert rows[0]["ip"] == "10.0.1.50"


def test_linux_syslog_parser():
    syslog_data = """Oct 24 02:10:00 municipal-sso sshd[1024]: Failed password for invalid user ops_k from 10.20.0.8 port 48291 ssh2
Oct 24 02:14:00 vpn-gateway openvpn[2048]: ops_k/8.8.8.8:1194 MULTI: Learn: 10.0.1.50 -> ops_k/8.8.8.8:1194 vpn login success
"""
    rows = parse_universal_log(syslog_data)
    assert len(rows) == 2
    assert rows[0]["event_type"] == "login_failure"
    assert rows[0]["account"] == "ops_k"
    assert rows[0]["ip"] == "10.20.0.8"
    assert rows[1]["event_type"] == "login_success"
