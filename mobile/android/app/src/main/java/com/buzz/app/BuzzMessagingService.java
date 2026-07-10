package com.buzz.app;

import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Intent;
import androidx.core.app.NotificationCompat;
import com.capacitorjs.plugins.pushnotifications.PushNotificationsPlugin;
import com.google.firebase.messaging.FirebaseMessagingService;
import com.google.firebase.messaging.RemoteMessage;
import java.util.Map;

public class BuzzMessagingService extends FirebaseMessagingService {

    @Override
    public void onMessageReceived(RemoteMessage remoteMessage) {
        Map<String, String> dados = remoteMessage.getData();
        if ("buzina_recebida".equals(dados.get("tipo"))) {
            exibirNotificacaoBuzina(remoteMessage, dados);
        }
        PushNotificationsPlugin.sendRemoteMessage(remoteMessage);
    }

    @Override
    public void onNewToken(String token) {
        PushNotificationsPlugin.onNewToken(token);
    }

    private void exibirNotificacaoBuzina(RemoteMessage remoteMessage, Map<String, String> dados) {
        String buzinaId = dados.get("buzina_id");
        String titulo = dados.get("titulo");
        String corpo = dados.get("corpo");
        String url = dados.get("url");

        if (titulo == null || titulo.isEmpty()) {
            titulo = remoteMessage.getNotification() != null
                ? remoteMessage.getNotification().getTitle()
                : "Buzz";
        }
        if (corpo == null) {
            corpo = remoteMessage.getNotification() != null
                ? remoteMessage.getNotification().getBody()
                : "";
        }

        Intent telaCheia = new Intent(this, BuzzBuzinaActivity.class);
        telaCheia.putExtra("buzina_id", buzinaId);
        telaCheia.putExtra("url", url);
        telaCheia.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);

        PendingIntent intentTelaCheia = PendingIntent.getActivity(
            this,
            buzinaId != null ? buzinaId.hashCode() : 0,
            telaCheia,
            PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
        );

        Intent toque = new Intent(this, MainActivity.class);
        toque.putExtra("buzina_id", buzinaId);
        toque.putExtra("url", url);
        toque.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);

        PendingIntent intentToque = PendingIntent.getActivity(
            this,
            buzinaId != null ? buzinaId.hashCode() + 1 : 1,
            toque,
            PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
        );

        NotificationCompat.Builder builder = new NotificationCompat.Builder(this, "buzz_chamada")
            .setSmallIcon(android.R.drawable.ic_dialog_alert)
            .setContentTitle(titulo)
            .setContentText(corpo)
            .setPriority(NotificationCompat.PRIORITY_MAX)
            .setCategory(NotificationCompat.CATEGORY_CALL)
            .setVisibility(NotificationCompat.VISIBILITY_PUBLIC)
            .setAutoCancel(true)
            .setContentIntent(intentToque)
            .setFullScreenIntent(intentTelaCheia, true)
            .setSound(
                android.net.Uri.parse("android.resource://" + getPackageName() + "/raw/buzina")
            )
            .setVibrate(new long[] { 0, 200, 100, 200, 100, 400 });

        NotificationManager gerenciador = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
        if (gerenciador != null) {
            int id = buzinaId != null ? buzinaId.hashCode() : (int) System.currentTimeMillis();
            gerenciador.notify(id, builder.build());
        }
    }
}
