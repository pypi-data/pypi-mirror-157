import React from "react";
import { Text, Button } from "@ui-kitten/components";
import { View } from "react-native";

export default class ScreenOne extends React.Component {
  constructor(props) {
    super(props);
    this.state = {};
  }

  name1 = () => alert("Bingo");

  render() {
    return (
      <View
        style={{
          height: "100%",
          justifyContent: "center",
          alignItems: "center",
          flex: 1,
        }}
      >
        <Text>Hello</Text>
        <Button onPress={() => this.name1()}>
          <Text>Press me</Text>
        </Button>
      </View>
    );
  }
}
