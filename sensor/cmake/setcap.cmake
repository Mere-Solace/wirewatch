execute_process(
	COMMAND sudo setcap cap_net_raw,cap_net_admin=eip "${BINARY}"
	RESULT_VARIABLE result
)
if(NOT result EQUAL 0)
  message(WARNING
    "Could not grant capture permissions. Run manually:\n"
    "  sudo setcap cap_net_raw,cap_net_admin=eip ${BINARY}")
endif()