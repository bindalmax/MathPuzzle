import 'package:flutter/material.dart';

class LeaderboardWidget extends StatelessWidget {
  final List<Map<String, dynamic>> scores;

  LeaderboardWidget({required this.scores});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: const [
            Expanded(child: Text('Player', style: TextStyle(fontWeight: FontWeight.bold))),
            Expanded(child: Text('Score', textAlign: TextAlign.center, style: TextStyle(fontWeight: FontWeight.bold))),
            Expanded(child: Text('Category', textAlign: TextAlign.right, style: TextStyle(fontWeight: FontWeight.bold))),
          ],
        ),
        const Divider(),
        ...scores.map((score) => Padding(
          padding: const EdgeInsets.symmetric(vertical: 4.0),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(child: Text(score['name'])),
              Expanded(child: Text('${score['score']}', textAlign: TextAlign.center)),
              Expanded(child: Text(score['category'], textAlign: TextAlign.right)),
            ],
          ),
        )).toList(),
      ],
    );
  }
}
